В проекте используется облачная база данных PostgreSQL (Работает постоянно). 
Однако для старта также требуется инициализация бд и парсера.
Они находятся в   
- __*./app/start/db_init*__ - (требуется для запуска впервые)
- __*./app/services/rabbit/parser_worker/parser_init*__ - (требуется для обновления сессии подключения)
