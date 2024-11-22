from datetime import datetime
from flask import Blueprint, request, jsonify, current_app as app
from flask_cors import cross_origin
from models import User, db, Trip, TripGuest, TripExpense, TripExpenseShare
from .utils import token_required, get_request_data, validate_user_trip

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/add-expense', methods=['POST'])
@cross_origin()
@token_required
def add_expense(token):
    
    app.logger.info("expenses/add-expense")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    expense_title = data['title']
    expense_amount = data['amount']

    users_involved = data['usersInvolved']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    try:
        expense_amount = float(expense_amount)
    except ValueError:
        app.logger.error("Invalid input. 400 Error")
        return jsonify({"error": "Invalid expense amount."}), 400
    
    # Add the expense to the trip
    try:
        new_expense = TripExpense(
            trip_id=trip_id,
            user_id=user_id,
            title=expense_title,
            amount=expense_amount,
            settled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(new_expense)
        db.session.flush()
        for user in users_involved:
            new_expense_share = TripExpenseShare(
                expense_id=new_expense.id,
                user_id=user['selectedUserId'],
                amount=user['amount'],
                trip_id=trip_id
            )
            db.session.add(new_expense_share)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error adding expense to trip: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while adding the expense to the DB."}), 500
    
    return jsonify({"message": "Expense added successfully."}), 201

@expenses_bp.route('/update-expense', methods=['PUT'])
@cross_origin()
@token_required
def update_expense(token):

    app.logger.info("expenses/update-expense")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']
    expense_id = data['expense_id']
    expense_title = data['title']
    expense_amount = data['amount']

    users_involved = data['usersInvolved']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    try:
        expense_amount = float(expense_amount)
    except ValueError:
        app.logger.error("Invalid input. 400 Error")
        return jsonify({"error": "Invalid expense amount."}), 400
    
    # Update the expense
    try:
        expense = TripExpense.query.filter_by(id=expense_id).first()
        if not expense:
            return jsonify({"error": "Expense not found."}), 404
        expense.title = expense_title
        expense.amount = expense_amount
        expense.updated_at = datetime.now()
        db.session.commit()
        
        # Update the expense shares
        for user in users_involved:
            expense_share = TripExpenseShare.query.filter_by(expense_id=expense_id, user_id=user['selectedUserId']).first()
            if not expense_share:
                new_expense_share = TripExpenseShare(
                    expense_id=expense_id,
                    user_id=user['selectedUserId'],
                    amount=user['amount'],
                    trip_id=trip_id
                )
                db.session.add(new_expense_share)
            else:
                expense_share.amount = user['amount']
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error updating expense: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while updating the expense."}), 500
    
    return jsonify({"message": "Expense updated successfully."}), 200

@expenses_bp.route('/get-expenses', methods=['GET'])
@cross_origin()
@token_required
def get_expenses(token):
    
    app.logger.info("expenses/get-expenses")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    # query the expenses table for all expenses associated with a trip
    expenses = TripExpense.query.filter_by(trip_id=trip_id).all()
    expense_list = []
    for expense in expenses:
        expense_shares = TripExpenseShare.query.filter_by(expense_id=expense.id).all()
        users_involved = []
        for share in expense_shares:
            user = User.query.filter_by(id=share.user_id).first()
            users_involved.append({
                "selectedUserId": user.id,
                "amount": share.amount,
                "firstName": user.first_name,
                "lastName": user.last_name
            })
        user = User.query.filter_by(id=expense.user_id).first()
        expense_list.append({
            "expenseId": expense.id,
            "settled": expense.settled,
            "title": expense.title,
            "amount": expense.amount,
            "createdDate": expense.created_at.strftime("%b %d"),
            "updatedDate": expense.created_at.strftime("%b %d"),
            "userId": expense.user_id,
            "userFirstName": user.first_name,
            "userLastName": user.last_name,
            "usersInvolved": users_involved
        })
    
    return jsonify({"expenses": expense_list}), 200

@expenses_bp.route('/delete-expense', methods=['DELETE'])
@cross_origin()
@token_required
def delete_expense(token):
    
    app.logger.info("expenses/delete-expense")
    data = get_request_data(token)
    app.logger.debug(data)
    
    user_id = data['user_id']
    expense_id = data['expense_id']
    trip_id = data['trip_id']

    valid, error = validate_user_trip(user_id, trip_id)
    if not valid:
        return jsonify({"message": f"Invalid user or trip id: {error}"}), 400
    
    expense = TripExpense.query.filter_by(id=expense_id).first()
    if not expense:
        return jsonify({"error": "Expense not found."}), 404
    
    expense_shares = TripExpenseShare.query.filter_by(expense_id=expense_id).all()
    
    # delete the expense
    try:
        db.session.delete(expense)
        for share in expense_shares:
            db.session.delete(share)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Error deleting expense: {e}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while deleting the expense."}), 500
    
    return jsonify({"message": "Expense deleted successfully."}), 200