
from website import create_app
from website.models import create_table

app = create_app()

if __name__ == "__main__":
    create_table()
    print("Tables created successfully!")
    app.run(debug=True)
