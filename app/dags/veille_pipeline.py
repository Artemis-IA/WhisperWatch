# app/dags/veille_pipeline.py

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from services.youtube_service import get_current_state
from services.rl_agent import ETDQNAgent
from tasks.scraping import start_scraping

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 9, 14),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'veille_pipeline',
    default_args=default_args,
    description='Pipeline de veille automatique avec RL-triggering',
    schedule_interval=timedelta(hours=1),
)

rl_agent = ETDQNAgent(state_size=10, action_size=2)

def decide_and_trigger():
    state = get_current_state()  # Fetch the current state of the YouTube environment
    action = rl_agent.choose_action(state)
    
    if action == 0:
        start_scraping()  # Start scraping task
    else:
        print("Skipping scraping for now...")
    
    rl_agent.send_decision(state, action)  # Send decision to Kafka

t1 = PythonOperator(
    task_id='monitor_new_videos',
    python_callable=get_current_state,
    dag=dag,
)

t2 = PythonOperator(
    task_id='trigger_pipeline',
    python_callable=decide_and_trigger,
    dag=dag,
)

t1 >> t2
