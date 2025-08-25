from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML template for the webpage
# It contains the CSS, video background, and calculator form.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Final Grade Calculator</title>
    <style>
        /* Reset margin/padding and set full height */
        html, body {
            margin: 0;
            padding: 0;
            height: 100%;
            font-family: Arial, sans-serif;
            overflow: auto;  /* allow scrolling */
        }

        /* Background video styling */
        #bg-video {
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;          /* keep it behind content */
            object-fit: cover;    /* scale & crop nicely */
        }

        /* Calculator container */
        .container {
            background-color: rgba(255, 255, 255, 0.95); /* semi-transparent white */
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
            max-width: 520px;
            width: 100%;
            margin: auto;
            position: relative;
            top: 50%;                /* vertically center */
            transform: translateY(-50%);
        }

        h2 { text-align: center; }

        /* Input fields and buttons */
        input, button {
            width: 100%;
            margin: 5px 0 15px 0;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }

        /* Button styles */
        button {
            background-color: #007BFF;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        button:hover { background-color: #0056b3; }

        /* Results section */
        .results { margin-top: 20px; text-align: left; }
        .error { color: red; font-weight: bold; }

        /* Table styles */
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    
    <video autoplay muted loop id="bg-video">
        <source src="https://admin.lofistudio.com/uploads/Assassin_s_12469565e0.webm" type="video/webm">
        Your browser does not support HTML5 video.
    </video>

    <!-- Main Color Box -->
    <div class="container">
        <h2>Final Grade Calculator</h2>

        <!-- Input Form -->
        <form method="post">
            <label>Number of Absences:</label>
            <input type="number" name="absences" min="0" value="{{ request.form.get('absences','') }}" required>

            <label>Prelim Exam Grade:</label>
            <input type="number" name="prelim_exam" min="0" max="100" value="{{ request.form.get('prelim_exam','') }}" required>

            <label>Quizzes Grade:</label>
            <input type="number" name="quizzes" min="0" max="100" value="{{ request.form.get('quizzes','') }}" required>

            <label>Requirements Grade:</label>
            <input type="number" name="requirements" min="0" max="100" value="{{ request.form.get('requirements','') }}" required>

            <label>Recitation Grade:</label>
            <input type="number" name="recitation" min="0" max="100" value="{{ request.form.get('recitation','') }}" required>

            <!-- Submit & Reset buttons -->
            <button type="submit">Calculate</button>
            <button type="reset" onclick="window.location.href='/'">Reset</button>
        </form>

        <!-- Error Message -->
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}

        <!-- Results -->
        {% if result %}
            <div class="results">
                <h3>Results:</h3>
                <p>{{ result|safe }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculate():
    result = ""
    error = ""

    if request.method == "POST":
        try:
            # ✅ Collect user input
            absences = int(request.form["absences"])
            prelim_exam = float(request.form["prelim_exam"])
            quizzes = float(request.form["quizzes"])
            requirements = float(request.form["requirements"])
            recitation = float(request.form["recitation"])

            # ✅ Input validation
            if absences < 0:
                error = "Absences cannot be negative."
            elif not (0 <= prelim_exam <= 100 and 0 <= quizzes <= 100 and 0 <= requirements <= 100 and 0 <= recitation <= 100):
                error = "Grades must be between 0 and 100."
            elif absences >= 4:
                # ✅ Fail if absences are 4 or more
                result = f"FAILED due to {absences} absences."
            else:
                # ✅ Attendance deduction (10 points per absence)
                attendance = max(0, 100 - (absences * 10))

                # ✅ Class Standing weighted average
                class_standing = (quizzes * 0.4) + (requirements * 0.3) + (recitation * 0.3)

                # ✅ Prelim Grade calculation
                prelim_grade = (prelim_exam * 0.6) + (attendance * 0.1) + (class_standing * 0.3)

                # ✅ Contributions to final grade formula
                prelim_contribution = prelim_grade * 0.2
                midterm_weight, finals_weight = 0.3, 0.5

                # ✅ Helper functions for grade requirements
                def needed_finals(target, midterm):
                    return (target - prelim_contribution - (midterm * midterm_weight)) / finals_weight

                def needed_midterm(target, finals):
                    return (target - prelim_contribution - (finals * finals_weight)) / midterm_weight

                # ✅ Table for Passing (75)
                table_passing = "<h4>Passing (75)</h4><table><tr><th>Midterm</th><th>Needed Finals</th></tr>"
                for mid in [60, 70, 75, 80, 85, 90]:
                    finals_needed = needed_finals(75, mid)
                    table_passing += f"<tr><td>{mid}</td><td>{finals_needed:.2f}</td></tr>"
                table_passing += "</table>"

                # ✅ Table for Dean’s Lister (90)
                table_dl = "<h4>Dean’s Lister (90)</h4><table><tr><th>Midterm</th><th>Needed Finals</th></tr>"
                for mid in [70, 80, 85, 90, 95]:
                    finals_needed = needed_finals(90, mid)
                    table_dl += f"<tr><td>{mid}</td><td>{finals_needed:.2f}</td></tr>"
                table_dl += "</table>"

                # ✅ Final result string with breakdown
                result = f"""
                Attendance: {attendance:.2f}<br>
                Class Standing: {class_standing:.2f}<br>
                Prelim Grade: {prelim_grade:.2f}<br><br>
                Overall = (20% Prelim) + (30% Midterm) + (50% Finals)<br><br>
                ✅ Breakdown for Passing (75) and Dean’s Lister (90):<br>
                {table_passing}
                {table_dl}
                """

        except ValueError:
            error = "Please enter valid numbers only."

    # ✅ Render HTML with results or error
    return render_template_string(HTML_TEMPLATE, result=result, error=error, request=request)

if __name__ == "__main__":

    app.run(debug=True)  # ✅ Debug mode for testing
