from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# MySQL database connection
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='890801',
    database='elections'
)
@app.route('/check_voter')
def render_check_voter_template():
    return render_template('index.html')

# Route for checking if the voter exists
@app.route('/check_voter', methods=['POST'])
def check_voter():
    data = request.json
    voter_id = data['voter_id']
    
    # Check if voter exists in the database
    cursor = connection.cursor()
    cursor.execute("SELECT Name FROM Voters WHERE Voter_ID = %s", (voter_id,))
    voter = cursor.fetchone()
    cursor.close()

    if voter is None:
        return jsonify({'error': 'Voter not found'}), 404
    else:
        voter_name = voter[0]  # Extract voter's name from the result
        return jsonify({'message': f'Voter {voter_name} found. Proceed to vote.'})

@app.route('/vote')
def render_vote_template():
    return render_template('cast_vote.html')

@app.route('/vote', methods=['POST'])
def cast_vote():
    data = request.json
    voter_id = data['voter_id']
    candidate_id = data['candidate_id']

    try:
        # Insert vote into Votes table
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Votes (Voter_ID, Candidate_ID) VALUES (%s, %s)", (voter_id, candidate_id))
        connection.commit()
        cursor.close()

        # Update Votes_Count for the candidate
        cursor = connection.cursor()
        cursor.execute("UPDATE Candidates SET Votes_Count = Votes_Count + 1 WHERE Candidate_ID = %s", (candidate_id,))
        connection.commit()
        cursor.close()

        return jsonify({'message': 'Vote cast successfully'})

    except mysql.connector.Error as err:
        if err.errno == 1644:  # Voter has already cast a vote
            return jsonify({'error': 'You have already cast your vote'}), 409
        else:
            return jsonify({'error': f'An error occurred while casting your vote: {err}'}), 500




if __name__ == '__main__':
    app.run(debug=True, port=8000)
