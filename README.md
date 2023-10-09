# fastApiProject
Учебный проект для освоения FastAPI и Postgres. Возможно не самая актуальная версия, т.к. дописывалась на другом устройстве
в src.database асинхронный генератор сессии для работы с БД, и синхронный, т.к. некоторые функции отказывались работать с асинхронным подключением
в src.main основная программа
в папке src.auth модули, которые реализовали основную функцию веб проекта, регистрация, авторизация, получение данных о пользователе, хедерсы, куки и айпи.
также там находятся модели обьектов БД
к проекту был подключен алембик, для миграций БД
