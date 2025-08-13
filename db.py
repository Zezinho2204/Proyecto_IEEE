from models import Base, engine

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos creada")

if __name__ == "__main__":
    init_db()
