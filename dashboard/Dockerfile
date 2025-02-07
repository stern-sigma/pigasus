FROM python:3.9.21-bookworm

WORKDIR /dashboard_

COPY requirements.txt /dashboard_

RUN pip3 install -r requirements.txt

COPY Dashboard.py /dashboard_

COPY graphs.py /dashboard_

COPY manager_graphs.py /dashboard_

COPY pages /dashboard_

EXPOSE 8501

CMD ["streamlit", "run", "Dashboard.py", "--server.port=8501"]


