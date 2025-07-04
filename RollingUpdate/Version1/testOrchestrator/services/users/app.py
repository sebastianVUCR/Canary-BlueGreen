from flask import Flask
from users import users_bp

from flasgger import Swagger

app = Flask(__name__)

swagger_template = {
    "info": {
        "title": "Test Orchestrator",
        "version": "1.0",
        "description": "Test orchestrator API.",
        "termsOfService": "https://www.testorchestrator.com/tos/",
        "version": "1.0",
        "contact": {
            "responsibleOrganization": "Sebastian org",
            "responsibleDeveloper": "Sebastian",
            "email": "sebastian.vargassoto@ac.cr",
            "url": "https://www.testorchestrator.com",
        },
    }
}

app.config['SWAGGER'] = {
    "specs_route": "/users/apidocs/"
}

swagger = Swagger(app, template=swagger_template)

app.register_blueprint(users_bp)


if __name__ == "__main__":
    app.run(debug=True)
