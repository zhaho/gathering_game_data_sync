#!/bin/bash
runuser -l ansible -c 'ansible-pull -o -U https://github.com/zhaho/gameDataToAPI.git' >> /var/log/ansible 2>&1
