# gathering_game_data_sync
This repo is deprecated and are now included in the gathering_service repo instead, which include all services for Gathering.

## API Integration with autoupdate through Ansible Pull

* Used for my personal Board Game Site for checking if some game data needs to be updated, based on the API from BGG

## Dependensies
* Ansible
* Git

## Installation
* Make sure the dependencies are installed
* Pull down the repo with:
```bash
ansible-pull -U https://github.com/zhaho/gameDataToAPI.git
```
* Now everything is set up in order to fetch which games that needs to be updated from Gathering, and check those games against BGG's API, and use my own Gathering API to push in the data. 

### Since the Ansible Pull job is checking for updated, it will update if self automatically when the repo is updated.
