# Running jobs that require large memory

Reservation of a standard node on Lonestar5 offers 64 GB memory and makes all of this memory available to the user, even if only running 1 task/thread (e.g. -N 1 -n 1). Memory needs can be profiled by the TACC module remora. Execute ```module load remora; module help remora``` for more information on profiling memory consumption.

Jobs that require more than 64 GB memory can be run using special compute nodes in Lonestar5. See https://portal.tacc.utexas.edu/user-guides/lonestar5#usinglargenodes-running for details on how to configure your interactive session or slurm job to run on the large memory nodes.

A brief overview is as follows:

1. Prior to running a session or job, load the TACC module required for large memory usage: ```module load TACC-largemem`.

2. Add a new directive in your slurm job script or pass a command line parameter to indicate usage of a large memory node. ```#SBATCH -p largemem512GB``` can be added to the directives in a slurm job script, or pass the following command line parameter to the sbatch or idev call: ```-p largemem512GB```.

3. When finished running on a large memory node, re-configure to default settings by executing ```module load TACC```.

Note if running a MPI job, the user must also load the impi-largemem TACC module prior to submitting the job.

# Activating a conda environment for largemem jobs

While on standard nodes the user can activate a conda environment on the login node prior to job script submission, our experience with the largemem nodes requires the environment activation call within the job script. The proper way to call this is to specify the `activate` executable explicitly: ```source $HOME/miniconda3/bin/activate ENVNAME```. Keep in mind that depending on which conda derivative you are using, the path to the `activate` executable may differ.
