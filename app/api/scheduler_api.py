# app/api/scheduler_api.py
from fastapi import APIRouter, HTTPException
from services.scheduler import scheduler
from apscheduler.triggers.interval import IntervalTrigger

router = APIRouter()

@router.post("/scheduler/start")
async def start_scheduler():
    try:
        scheduler.start()
        return {"message": "Scheduler started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")

@router.post("/scheduler/stop")
async def stop_scheduler():
    try:
        scheduler.stop()
        return {"message": "Scheduler stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")

@router.post("/scheduler/add_job")
async def add_job(job_id: str, interval_minutes: int):
    try:
        # You can define any function to schedule here
        def example_task():
            print(f"Executing scheduled job {job_id} at {datetime.now()}")

        scheduler.add_job(
            example_task,
            IntervalTrigger(minutes=interval_minutes),
            job_id=job_id,
            name=f"Job {job_id} every {interval_minutes} minutes",
            replace_existing=True
        )
        return {"message": f"Job '{job_id}' added with interval {interval_minutes} minutes."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding job: {str(e)}")

@router.post("/scheduler/remove_job")
async def remove_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Job '{job_id}' removed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing job: {str(e)}")

@router.get("/scheduler/jobs")
async def get_jobs():
    jobs = scheduler.get_jobs()
    job_list = [{"id": job.id, "name": job.name, "next_run_time": job.next_run_time} for job in jobs]
    return {"jobs": job_list}
