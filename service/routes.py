"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """
    List all accounts
    This endpoint will search and returns accounts list in the body of response
    """
    app.logger.info("Search for all accounts")
    accounts = Account.all()
    list_accounts = []
    for account in accounts:
        list_accounts.append(account.serialize())
    return make_response(
        jsonify(list_accounts), status.HTTP_200_OK
    )

######################################################################
# READ AN ACCOUNT
######################################################################

@app.route("/accounts/<account_id>", methods=["GET"])
def read_account(account_id):
    """
    Read an account with its ID from database
    This endpoint will search and returns account data in the body of response
    """
    app.logger.info("Search for an account with given ID")
    status_code = None
    return_data = {}
    try:
        account = Account.find(account_id)
        return_data = account.serialize()
        status_code = status.HTTP_200_OK
    except Exception:
        status_code = status.HTTP_404_NOT_FOUND  
        return_data["error"] = "Account ID "+str(account_id) +" not found"  

    return make_response(
        jsonify(return_data), status_code
    )


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<account_id>", methods=["PUT"])
def update_account(account_id):
    """
    Update an account already saved in the database
    This endpoint will search and returns account data in the body of response
    """
    app.logger.info("Search for an account with given ID")
    status_code = None
    return_data = {}
    account = Account.find(account_id)        
    if type(account) == Account :        
        prepare_data = account.deserialize(request.get_json())
        prepare_data.update()
        status_code = status.HTTP_200_OK
        return_data = account.serialize()
    else:
        status_code = status.HTTP_404_NOT_FOUND  
        raise ValueError("Account ID "+str(account_id) +" not found")  

    return make_response(
        jsonify(return_data), status_code
    )

######################################################################
# DELETE AN ACCOUNT
######################################################################

@app.route("/accounts/<account_id>", methods=["DELETE"])
def delete_account(account_id):
    """
    Delete an account with from the database
    This endpoint will search and removes account data
    """
    app.logger.info("Search for an account with given ID")
    status_code = None
    return_data = {}
    account = Account.find(account_id)
    if type(account) == Account :        
        account.delete()
        status_code = status.HTTP_204_NO_CONTENT
    else:
        raise ValueError("Account ID " + str(account_id) + " not found")

    return make_response(
        jsonify(return_data), status_code
    )

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
