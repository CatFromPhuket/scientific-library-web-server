import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app
import models
import schemas

# ========== Тестовая БД (SQLite в памяти) ==========

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Подменяем зависимость get_db на тестовую БД
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Создаём клиент
client = TestClient(app)


# ========== Фикстуры: подготовка и очистка БД ==========

@pytest.fixture(autouse=True)
def setup_db():
    """Перед каждым тестом: создаём таблицы заново (чистая БД)"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ========== Вспомогательная функция: создать пользователя и получить токен ==========

def register_and_login(username="testuser", password="testpass", role="reader"):
    """Регистрирует пользователя, вручную ставит роль и возвращает токен"""
    client.post("/register", json={"username": username, "password": password})

    # Вручную меняем роль в БД, если нужен админ
    if role == "admin":
        db = TestingSessionLocal()
        user = db.query(models.User).filter(models.User.username == username).first()
        user.role = "admin"
        db.commit()
        db.close()

    # Логинимся
    response = client.post("/login", json={"username": username, "password": password})
    return response.json()["access_token"]


# ========== ТЕСТЫ ==========

# ---------- CRUD: Scientists ----------

def test_create_scientist_unauthorized():
    """Без токена — 401"""
    response = client.post("/scientists/", json={
        "name": "Эйнштейн",
        "affiliation": "Принстон",
        "specialization": "Физика"
    })
    assert response.status_code == 401


def test_create_scientist_authorized():
    """С токеном — 200"""
    token = register_and_login()
    response = client.post(
        "/scientists/",
        json={"name": "Эйнштейн", "affiliation": "Принстон", "specialization": "Физика"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Эйнштейн"
    assert data["id"] is not None


def test_get_scientists():
    """Получение списка учёных (открытый)"""
    token = register_and_login()
    client.post(
        "/scientists/",
        json={"name": "Ньютон"},
        headers={"Authorization": f"Bearer {token}"}
    )
    response = client.get("/scientists/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_scientist_not_found():
    """Несуществующий учёный — 404"""
    response = client.get("/scientists/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Scientist not found"


# ---------- CRUD: Papers ----------

def test_create_paper():
    """Создание статьи (с токеном)"""
    token = register_and_login()

    # Создаём учёного и тему
    s = client.post(
        "/scientists/",
        json={"name": "Эйнштейн"},
        headers={"Authorization": f"Bearer {token}"}
    )
    scientist_id = s.json()["id"]

    t = client.post(
        "/topics/",
        json={"name": "Физика"},
        headers={"Authorization": f"Bearer {token}"}
    )
    topic_id = t.json()["id"]

    # Создаём статью
    response = client.post(
        "/papers/",
        json={
            "title": "Теория относительности",
            "year": 1905,
            "citations": 100,
            "scientist_id": scientist_id,
            "topic_id": topic_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Теория относительности"
    assert response.json()["scientist"]["name"] == "Эйнштейн"
    assert response.json()["topic"]["name"] == "Физика"


# ---------- Auth ----------

def test_register():
    """Регистрация нового пользователя"""
    response = client.post("/register", json={"username": "newuser", "password": "secret"})
    assert response.status_code == 200
    assert response.json()["username"] == "newuser"
    assert response.json()["role"] == "reader"


def test_register_duplicate():
    """Повторная регистрация — 400"""
    client.post("/register", json={"username": "dup", "password": "123"})
    response = client.post("/register", json={"username": "dup", "password": "123"})
    assert response.status_code == 400


def test_login():
    """Успешный вход"""
    client.post("/register", json={"username": "loginuser", "password": "pass"})
    response = client.post("/login", json={"username": "loginuser", "password": "pass"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password():
    """Неверный пароль — 401"""
    client.post("/register", json={"username": "bad", "password": "correct"})
    response = client.post("/login", json={"username": "bad", "password": "wrong"})
    assert response.status_code == 401


# ---------- Роли ----------

def test_delete_as_reader_forbidden():
    """Читатель не может удалять — 403"""
    token = register_and_login(role="reader")

    s = client.post(
        "/scientists/",
        json={"name": "Учёный"},
        headers={"Authorization": f"Bearer {token}"}
    )
    scientist_id = s.json()["id"]

    response = client.delete(
        f"/scientists/{scientist_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_delete_as_admin():
    """Админ может удалять — 200"""
    token = register_and_login(username="adminuser", role="admin")

    s = client.post(
        "/scientists/",
        json={"name": "Жертва"},
        headers={"Authorization": f"Bearer {token}"}
    )
    scientist_id = s.json()["id"]

    response = client.delete(
        f"/scientists/{scientist_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


# ---------- Бизнес-задача: рейтинг ----------

def test_scientist_rating():
    """Рейтинг учёного считается правильно"""
    token = register_and_login()

    s = client.post(
        "/scientists/",
        json={"name": "Бор"},
        headers={"Authorization": f"Bearer {token}"}
    )
    scientist_id = s.json()["id"]

    t = client.post(
        "/topics/",
        json={"name": "Квантовая физика"},
        headers={"Authorization": f"Bearer {token}"}
    )
    topic_id = t.json()["id"]

    # Две статьи: 10 и 30 цитирований
    client.post(
        "/papers/",
        json={"title": "Статья 1", "citations": 10, "scientist_id": scientist_id, "topic_id": topic_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    client.post(
        "/papers/",
        json={"title": "Статья 2", "citations": 30, "scientist_id": scientist_id, "topic_id": topic_id},
        headers={"Authorization": f"Bearer {token}"}
    )

    response = client.get(f"/scientists/{scientist_id}/rating")
    assert response.status_code == 200
    data = response.json()
    assert data["total_papers"] == 2
    assert data["total_citations"] == 40
    assert data["avg_citations_per_paper"] == 20.0
    assert data["rating"] == 40.0


def test_rating_no_papers():
    """Учёный без статей — рейтинг 0"""
    token = register_and_login()

    s = client.post(
        "/scientists/",
        json={"name": "Новичок"},
        headers={"Authorization": f"Bearer {token}"}
    )
    scientist_id = s.json()["id"]

    response = client.get(f"/scientists/{scientist_id}/rating")
    assert response.status_code == 200
    data = response.json()
    assert data["total_papers"] == 0
    assert data["rating"] == 0.0