import connexion

# Create the application instance
app = connexion.FlaskApp(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')

@app.route('/')
def index():
    return 'WebPOSHost V1.0'

# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6123, debug=True)