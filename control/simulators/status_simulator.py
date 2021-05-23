from control.simulators.distributions import Poisson

from control.managers.virtual_machine import VirtualMachine
from control.managers.cloud_manager import CloudManager

import time
import logging

from datetime import datetime, timedelta

import threading


class Sim:
    HIBERNATION_SIM = 'hibernation'
    REVOCATION_SIM = 'revocation'


class HibernationSim:

    def __init__(self, hibernation_rate, resume_rate):
        self.hibernation_rate = hibernation_rate
        self.resume_rate = resume_rate

        logging.info("<HibernationSim>: Hibernation rate: {} Resume rate: {}".format(
            self.hibernation_rate,
            self.resume_rate
        ))

        self.running = True

        self.threads = []
        self.deluded_vms = {}

    def __run(self, type: str, hib_model: Poisson, resume_model: Poisson):

        global_state = CloudManager.RUNNING
        # hibernate_now = False
        # resume_now = False

        while self.running:

            # list of vms that have to be removed
            finished_vms = []
            time.sleep(1)

            # Step 1: define the global_state
            # if global_state is running check if a hibernation occurs
            if global_state == CloudManager.RUNNING:
                if hib_model.event_happened():
                    # if hibernate_now:
                    global_state = CloudManager.HIBERNATING

            # if global_state is Hibernated check if a resume occurs
            elif global_state == CloudManager.HIBERNATED:
                if resume_model.event_happened():
                    # if resume_now:
                    global_state = CloudManager.RUNNING

            # check to verify if a hibernation occurs
            hibernation_occurs = False

            #  Step 2: update VMs' state
            # for each VM; do
            for vm in self.deluded_vms[type]:
                vm: VirtualMachine

                # get the real state of the VM
                real_state = vm.manager.get_instance_status(vm.instance_id)

                if real_state == CloudManager.RUNNING:

                    if global_state == CloudManager.HIBERNATING:
                        # wait until vm is ready
                        while not vm.ready:
                            time.sleep(5)

                        # Starting hibernation Process
                        vm.current_state = CloudManager.HIBERNATED
                        vm.hibernation_process_finished = False
                        hibernation_occurs = True

                        logging.info("<Simulator>: Hibernating VM {} type {} timestamp: {}".format(
                            vm.instance_id,
                            vm.instance_type.type,
                            datetime.now()
                        ))
                    else:
                        vm.current_state = global_state

                else:
                    # global_state = CloudManager.RUNNING
                    if real_state is None:
                        real_state = CloudManager.PENDING

                    vm.current_state = real_state

                # Check if the VM has stop and has to be removed
                if vm.current_state in (CloudManager.STOPPED,
                                        CloudManager.STOPPING,
                                        CloudManager.SHUTTING_DOWN,
                                        CloudManager.TERMINATED) or vm.failed_to_created:
                    finished_vms.append(vm)

            # Step 3: remove the vms that has finished
            # remove the finished VMS
            for vm in finished_vms:
                self.deluded_vms[type].remove(vm)

            # Step 4: Check if a new hibernation happened

            # if a new hibernation happened wait until all vm finished the hibernation process
            if global_state == CloudManager.HIBERNATING and hibernation_occurs:

                # check if all VMs finished the hibernation process
                finished = False

                while not finished:
                    # wait until the hibernation finish
                    finished = True

                    time.sleep(5)
                    # check if all vms has finished the hibernation process
                    for vm in self.deluded_vms[type]:
                        if not vm.hibernation_process_finished and vm.state != CloudManager.TERMINATED:
                            finished = False

                # change the global state to HIBERNATED
                global_state = CloudManager.HIBERNATED

        for vm in self.deluded_vms[type]:
            vm.in_simulation = False

    def stop_simulation(self):
        logging.info("Stopping simulation..")
        self.running = False

        for thread in self.threads:
            thread.join()

        logging.info("Simulation stopped")

    def register_vm(self, vm: VirtualMachine):
        # set vm's simulation flag
        vm.in_simulation = True

        # check if it already has instances from the same type
        if vm.type not in self.deluded_vms:
            self.deluded_vms[vm.type] = []

            # create new Models
            hib_model = Poisson(plambda=self.hibernation_rate)
            resume_model = Poisson(plambda=self.resume_rate)

            # create a thread to simulate the states of the new VM type
            thread = threading.Thread(target=self.__run, args=[vm.type, hib_model, resume_model])
            thread.start()
            self.threads.append(thread)

        # update the dict with the deluded vms
        self.deluded_vms[vm.instance_type.type].append(vm)


class RevocationSim:

    def __init__(self, termination_rate):
        self.rate = termination_rate

        logging.info("<TerminationSim>: Termination rate: {}".format(
            self.rate,
        ))

        self.running = True

        self.threads = []

    def __run(self, vm: VirtualMachine, model: Poisson):
        while not vm.ready:
            time.sleep(1)

        while self.running:

            time.sleep(1)

            # if global_state is running check if a termination occurs
            if vm.state == CloudManager.RUNNING and vm.ready:
                if model.event_happened():
                    vm.terminate(delete_volume=False)
                    return

    def stop_simulation(self):
        logging.info("Stopping simulation..")
        self.running = False

        for thread in self.threads:
            thread.join()

        logging.info("Simulation stopped")

    def register_vm(self, vm: VirtualMachine):
        # create a new Models
        model = Poisson(plambda=self.rate)

        # create a thread to simulate the states of the new VM type
        thread = threading.Thread(target=self.__run, args=[vm, model])
        thread.start()
        self.threads.append(thread)
