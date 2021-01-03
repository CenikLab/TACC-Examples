# Mozart

Mozart is the main computational server of our lab. It is intended to be used for parallel jobs requiring large amounts of memory and cores.

Mozart has a CPU with 64 cores. It has 256 GB of RAM and 51 TB of storage.

Please read the rest of this document before using Mozart.

## System Specifications

| | |
|------|--------|
| **CPU** | AMD Threadripper 3990X, 64 Core (2.9 GHz base 4.3 GHz Max ) |
|**Ram:** | 256 GB DDR 3600 MHz |
|**Storage (OS)**| 2 TB NVME |
|**Storage (HOME)**| 2 TB NVME |
|**Storage (Fast)**| 15 TB, Raid 0, SSD |
|**Storage (Archival)**| 51 TB  |
|**Network**| 10 Gbit Ethernet |
|**Operating System**| Ubuntu 20.04 |  


## Access

You can access Mozart via ssh over
[Lonestar5](https://github.com/CenikLab/TACC-Examples/tree/master/lonestar5) or
[Stampede2](https://github.com/CenikLab/TACC-Examples/tree/master/stampede2) head nodes **ONLY**.

*Mozart is behind firewalls and therefore you won't be able to access it from other locations.*

```
ssh username@123.45.67.8
```

For the actual IP of Mozart, ask Hakan.

### An Access Shortcut

Let `username` be your username and `IP` be the actual IP address of Mozart.

Add the following line to your bash profile
(~/.bashrc or ~/.bash_profile)

```
alias mozart='ssh username@IP'
```

Log out and log in back (or, instead, run `source ~/.bashrc`). Then you'll be able to access Mozart after typing `mozart` in the terminal, followed by your password.

## Obtaining Account

Please contact Hakan for account related issues.

## Storage

Mozart has 3 tiers of storage;
**home**, **scratch** and **archive**.  Each type of storage is intended for a different purpose. So, it is very important to use the storage accordingly. Also, deleting or moving unused files and keeping a low footprint of space usage is crucial as Mozart is used by other lab members as well.

The storage tiers of Mozart are explained in detail below.

**NO STORAGE IS BACKED UP. IT IS THE USERS'  RESPONSIPILITY TO TAKE REGULAR BACKUPS AS NEEDED!**

### Home

This storage is in a 2 TB NVME solid state disk.

Every user has a home folder at `$HOME`. This folder is intended for

* Scripts, executables, git repositories, etc.
* Small files ( < 100 MB).
* Configuration files

Note that `$HOME` is the default working directory upon login.

Since `$HOME` has relatively smaller capacity, it is NOT intended for storing large files or carrying out read and / or  write (IO) intensive tasks.

Users must keep their `$HOME` usage below 50 GB.

### Scratch

Scratch is a Raid 0 array of solid state disks of capacity 14 TB.

Every user has a folder in scratch located at `$SCRATCH`. The path of this folder is
`/scratch/users/$USER`.

`$SCRATCH` can handle heavy IO. Therefore, data must be read from and written to scratch when running pipelines.

### Archive

Archive is an array of high capacity magnetic disks of size 49 TB.

Every user has a folder in archive located at `$ARCHIVE`. The path of this folder is
`/archive/users/$USER`.

`$ARCHIVE` has a substantially slower IO performance compared to `$SCRATCH`. Therefore it is suitable for infrequent IO operations.

For example, at the very beginning of a pipeline, data is read from `$ARCHIVE` once. All intermediate files are written to / read from `$SCRATCH` and the end-product of the pipeline is written to `$ARCHIVE`.

## Software

Software installation should be done using
[conda](https://docs.conda.io/projects/conda/en/latest/index.html).

## Policies

   1. This system can ONLY be used for research & educational purposes involving the lab projects. Any other type of usage is strictly forbidden.  

   2. Keep your `$HOME` usage below 50 GB.

   3. Do NOT use more than 32 cores simultaneously. If you need to use all 64 cores, please coordinate with other users.

   4. Keep your memory footprint below 64 TB. If you need to use more memory, please coordinate with other users.

   5. Do NOT share your password with another person or let another person to use Mozart.

   6. Use a strong [password](https://its.lafayette.edu/policies/strongpasswords/).

   7. Always watch for your storage usage of all types. The command `df -hs /path/to/folder` will tell you the total size of the folder.


### Running Jobs

Currently, no third party job schedulers exist in Mozart. All jobs are directly handled by the operating system. So, the pipelines or executables should be run directly on the command line.

## Screen

For long time consuming executions, jobs, pipelines etc., users are **strongly encouraged** to use the [screen](https://linuxize.com/post/how-to-use-linux-screen/) command. This allows users to logout from TACC and login back again and go to their running jobs.

## Questions

For questions or requests, contact Hakan.
