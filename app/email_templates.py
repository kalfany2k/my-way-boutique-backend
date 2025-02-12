WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bine ai venit pe MWB!</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
            text-transform: uppercase;
            -webkit-text-stroke: 1px #2c3e50;
            text-stroke: 1px #2c3e50;
            margin: 0;
        }}
        .message {{
            text-align: center;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #777;
            border-top: 1px solid #ddd;
            padding-top: 20px;
            margin-top: 30px;
        }}
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MWB</h1>
        </div>
        <div class="message">
            <p>Bine ai venit pe MWB, <strong>{name}</strong>!</p>
            <p>Îți dorim o experiență cât mai plăcută.</p>
        </div>
        <div class="footer">
            <p>Dacă ai întrebări sau ai nevoie de asistență, nu ezita să ne contactezi:</p>
            <p>Email: <a href="mailto:support@mwb.com">support@mwb.com</a></p>
            <p>Telefon: +40 123 456 789</p>
            <p>Website: <a href="https://www.mwb.com">www.mwb.com</a></p>
        </div>
    </div>
</body>
</html>
"""