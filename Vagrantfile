# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # vbox name
  config.vm.box = "ubuntu/xenial64"

  # port forwarding
  config.vm.network :forwarded_port, guest: 443, host: 8443

  config.vm.network "private_network", ip: "192.168.50.4"
  config.vm.provision 'shell', inline: "sudo apt-get install python --yes"

  # shared folders
  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/playbook.yml"
    ansible.groups = {
      "vagrant" => ["default"]
    }
#    ansible.vault_password_file = "../dc-law-private/ansible/get_vagrant_vault_password"
  end

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end
end
