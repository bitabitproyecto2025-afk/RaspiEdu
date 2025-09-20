Objetivo General
1.Reducir la brecha tecnológica en la comunidad educativa República de Argentina mediante el diseño e implementación de un aplicativo sustentado en la autogestión, que garantice su sostenibilidad en el tiempo.

Objetivos Específicos 
1.Identificar las necesidades tecnológicas y roles de los actores de la comunidad educativa, a través de un proceso participativo de autodiagnóstico
2.Diseñar un dispositivo de almacenamiento que esté adaptado al contexto escolar, el cual facilite el acceso equitativo a recursos digitales y fomente la alfabetización tecnológica
3.Implementar un modelo de gestión comunitaria que asegure la sostenibilidad económica, técnica y social 

Backend: FastAPI + Uvicorn, ORM: SQLModel (SQLite), Auth: JWT.

Frontend: HTML ligero + Jinja2 + Alpine.js. Sin frameworks pesados.

Servidor estático: Nginx al frente como reverse proxy y caché.

DB: SQLite en volumen. Suficiente para ~20 concurrentes.

Contenedores: nginx + app (FastAPI). Multi-arch (armv7/arm64/amd64).

Compatibilidad: Diseñado para Raspberry Pi hoy y cualquier micro-PC mañana.

Repositorios y CI: GitHub + buildx para imágenes multi-arquitectura.
