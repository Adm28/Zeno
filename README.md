# Zeno

Zeno is a resource allocator for distributed deep learning jobs.
Deep learning jobs are time consuming and resource intensive. Today there are numerous schedulers and resource allocators whose primary ambition is to minimise the total completetion time of all jobs and neglect the fairness of hardware resources allocated for each job.

Zeno tries to tackle this problem by striking the balance between average waiting time and job execution time.
Zeno engine primarily consists of epoch estimator and custom scheduler.





