# jenkins-restore

Mass Jenkins jobs configuration restore.

## Problem

Let you have a large number of CI-jobs that need to be reset to some identical configuration.

## Solution

 0. Get names of CI-jobs to restore
 1. Fill file with any name with them
 2. Export your ethalon configuration (`<YOUR_JOB_URL>/config.xml`)
 3. Edit `params.conf`. Set your username, password, ethalon config file and file with CI-jobs to restore
 4. Run with Python 2.x: `python reserve.py @params.conf`

## Unlicense

This is a public domain. Do whatever you want with this code.
