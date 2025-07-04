from flask import Flask
from orchestrator import testOrchestrator_bp

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
    "specs_route": "/tasks/apidocs/"
}

swagger = Swagger(app, template=swagger_template)

app.register_blueprint(testOrchestrator_bp)


if __name__ == "__main__":
    app.run(debug=True)
