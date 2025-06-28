from flask import Flask
from serverAdministrator import serverAdministrator_bp
from log_utils import init_logging
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

swagger = Swagger(app, template=swagger_template)

init_logging()
app.register_blueprint(serverAdministrator_bp)


if __name__ == "__main__":
    app.run(debug=True)
