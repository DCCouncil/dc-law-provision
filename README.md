Provisioning for DC Code servers
================================

This repo manages search.code.dccouncil.us.

Development
-----------
1. Install vagrant
1. Install ansible
1. run `vagrant up` from the repo root

Production
----------
1. ensure `dc-law-provision-private` is cloned as sibling to this repo.
1. install ansible
1. run `ansible-playbook -i inventories/production playbook.yml --ask-vault-pass` from the ansible directory

`dc-law-provision-private` should have the following directory structure:

    - ansible
    |- group_vars
     |- production
      |- private.yaml
    |- inventories
     |- production

Symlinks in `dc-law-provision` point to the appropriate files in `dc-law-provision-private`. 