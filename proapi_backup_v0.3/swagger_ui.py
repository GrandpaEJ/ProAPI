"""
Swagger UI module for ProAPI framework.

Provides Swagger UI for API documentation.
"""

# Swagger UI version
SWAGGER_UI_VERSION = "5.9.0"

# Swagger UI HTML template
SWAGGER_UI_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@{version}/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}

        *,
        *:before,
        *:after {{
            box-sizing: inherit;
        }}

        body {{
            margin: 0;
            background: #fafafa;
        }}

        .swagger-ui .topbar {{
            background-color: #2c3e50;
        }}

        .swagger-ui .topbar .download-url-wrapper .select-label select {{
            border-color: #3498db;
        }}

        .swagger-ui .info .title {{
            color: #2c3e50;
        }}

        .swagger-ui .opblock.opblock-get .opblock-summary-method {{
            background-color: #61affe;
        }}

        .swagger-ui .opblock.opblock-post .opblock-summary-method {{
            background-color: #49cc90;
        }}

        .swagger-ui .opblock.opblock-put .opblock-summary-method {{
            background-color: #fca130;
        }}

        .swagger-ui .opblock.opblock-delete .opblock-summary-method {{
            background-color: #f93e3e;
        }}

        .swagger-ui .opblock.opblock-patch .opblock-summary-method {{
            background-color: #50e3c2;
        }}

        .swagger-ui .btn.execute {{
            background-color: #3498db;
            color: #fff;
            border-color: #3498db;
        }}

        .swagger-ui .btn.execute:hover {{
            background-color: #2980b9;
        }}

        .swagger-ui section.models {{
            border-color: #e8e8e8;
        }}

        .swagger-ui section.models.is-open h4 {{
            border-bottom-color: #e8e8e8;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>

    <script src="https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@{version}/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            // Get the current URL and construct the absolute URL for the spec
            const baseUrl = window.location.protocol + '//' + window.location.host;
            const specUrl = baseUrl + "{spec_url}";

            const ui = SwaggerUIBundle({{
                url: specUrl,
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                defaultModelRendering: 'model',
                displayRequestDuration: true,
                docExpansion: 'list',
                filter: true,
                showExtensions: true,
                showCommonExtensions: true,
                syntaxHighlight: {{
                    activate: true,
                    theme: "agate"
                }},
                tryItOutEnabled: true
            }});

            window.ui = ui;
        }};
    </script>
</body>
</html>
"""
