# epgp_diff

Check difference between 2 epgp backups. Scans logs created after the appearance of the 1st backup and adds all changes to the EP and GP values ​​from the 1st backup, checks whether the received values ​​are equal to the EP and GP values ​​in the 2nd backup.

Tested with EPGP version [5.5.19](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/epgp/epgp-5.5.19.zip).

## Quick Start

1. Clone repo and go to folder with script:

```git clone git@github.com:xAlexXxanderx/epgp_diff.git```

```cd epgp_diff```

2. Copy ``.env.dist`` as ``.env`` and fill it:

```cp .env.dist .env```

```editor .env```

3. Install requirements:

```pip install -r requirements.txt```

4. Start script:

```python3 main.py```

## List of used sources

 - https://github.com/Barsoomx/epgp_backup (work with epgp db files)
