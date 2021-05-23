import argparse

import subprocess

from pathlib import Path

command = "sh exec.sh fasta/{} fasta/{}  work.tmp_{} output_{}"

backup_file = 'exec.bkp'


def start_execution(ref, sequences):
    i = pos = 0
    # Verify if there is a exec.backup file to recovery the last execution position

    bkp = Path(backup_file)
    if bkp.is_file():
        # recovery
        with open(bkp, 'r') as bkp_fp:
            i = pos = int(bkp_fp.read())

    print("Pos: {}".format(pos))

    for seq in sequences[pos:]:
        # create cmd
        cmd = command.format(ref, seq, i, i)
        print(cmd)
        r = subprocess.run(cmd.split())

        # print(r.stdout)
        if r.returncode != 0:
            exit(r.returncode)

        i += 1
        # record execution position
        with open(bkp, 'w') as bkp_fp:
            bkp_fp.write('{}'.format(i))


def main():
    parser = argparse.ArgumentParser(description='Execute a list of commands')

    parser.add_argument('-r', '--ref', type=str, help='The reference sequence', required=True)

    parser.add_argument('-s', '--seq', nargs='+',
                        help='A list with all sequence files that will be compared', required=True)

    args = parser.parse_args()

    ref = args.ref
    sequences = args.seq

    start_execution(ref, sequences)


if __name__ == "__main__":
    main()
