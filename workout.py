from flask import Flask, render_template, request, jsonify
import anthropic
import os
from functools import wraps
from collections import deque
import time

app = Flask(__name__)
app.config['APPLICATION_ROOT'] = '/workout'

workout_styles = ["AMRAP", "For Time", "EMOM"]
equipment = sorted(["Barbell", "Kettlebell", "Bodyweight", "Dumbbell", "Jump Rope", "Pull-up Bar", "Bike Erg"])
durations = range(2, 31)

# Rate limiting setup
RATE_LIMIT = 3
RATE_LIMIT_PERIOD = 60  # 1 minute in seconds
request_timestamps = deque()

def rate_limited(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()

        # Remove timestamps older than the rate limit period
        while request_timestamps and current_time - request_timestamps[0] > RATE_LIMIT_PERIOD:
            request_timestamps.popleft()

        if len(request_timestamps) >= RATE_LIMIT:
            return jsonify({"error": "Rate limit exceeded. Please try again in 1 minute."}), 429

        request_timestamps.append(current_time)
        return func(*args, **kwargs)
    return wrapper

@app.route('/workout/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return generate_workout_handler()
    return render_template('index.html', styles=workout_styles, equipment=equipment, durations=durations, loading=False)

@rate_limited
def generate_workout_handler():
    style = request.form.get('style')
    equip = request.form.getlist('equipment')
    duration = request.form.get('duration')

    try:
        workout = generate_workout(style, equip, duration)
        return jsonify({"success": True, "workout": workout})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def generate_workout(style, equip, duration):
    import anthropic
    import os

    # Get the Anthropic API key from environment variables
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("No API key found. Please set the ANTHROPIC_API_KEY environment variable.")

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""
Human: Generate a Crossfit-style workout with the following parameters:
Style: {style}
Equipment: {', '.join(equip)}
Duration: {duration} minutes

Just post the raw workout, no preamble or other text, no warmup or cooldown. Print each exercise on a new line. Use all the equipment that was provided. Always mention the number of rounds, reps, and rest time.

Assistant:
"""

    try:
        response = client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=150
        )
        workout = response.completion.strip()  # Remove any leading/trailing whitespace
    except Exception as e:
        workout = f"Error generating workout: {str(e)}"

    return workout


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)