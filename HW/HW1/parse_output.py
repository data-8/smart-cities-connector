#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta


def adjust_score(score, category, submitted_at, deadline, full_cutoff=None,
                 partial_cutoff=None, max_score=None):
    """Adjusts the score depending on checkpoints met, as well as the
    assignment category. Outputs the adjusted score, along with the reason
    behind the applied adjustment.
    """
    early, cutoff, reason = None, None, ''

#    if category == 'lab':
#        if full_cutoff is not None and score >= full_cutoff:
#            score = 1
#        else:
#            score = 0
#
#        lock = deadline + timedelta(minutes=31)
#    elif category == 'hw' or category == 'vitamin':
#        if full_cutoff is not None and score >= full_cutoff:
#            score = max_score
#        elif partial_cutoff is not None and score >= partial_cutoff:
#            score = max_score * 0.5
#        else:
#            score = 0
#
#        lock = deadline + timedelta(minutes=31)
#    elif category == 'proj':
#        early = deadline - timedelta(days=1) + timedelta(hours=1)
#        cutoff = deadline + timedelta(hours=1)
#        lock = deadline + timedelta(days=1)
#
#        if early and submitted_at <= early:
#            score += 1
#            reason = 'Early Submission. Bonus Point Included'
#    elif category == 'quiz':
#        if full_cutoff is not None and score >= full_cutoff:
#            score = max_score
#        else:
#            score = 0
#
#        lock = deadline + timedelta(minutes=5)
#    elif category == 'generic':
#        lock = deadline + timedelta(minutes=5)
#
#    if submitted_at > lock:
#        score = 0
#        reason = 'Late Submission - No Credit'
#    elif cutoff and submitted_at > cutoff:
#        score = int(score * 2 / 3)
#        reason = 'Late Submission - Maximum Score: 2/3 * Score'

    return score, reason


def valid_date(s):
    """Checks if a date is in the valid format %m/%d/%Y. Offsets it by a
    constant amount to fix it at a minute before midnight.
    """
    try:
        offset = timedelta(hours=23, minutes=59, seconds=59)
        return datetime.strptime(s, "%m/%d/%Y") + offset
    except ValueError:
        msg = "Not a valid date: '{}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def parse_ok_output(output):
    point_breakdown = []
    reversed_list = output.splitlines()[::-1]
    score_lines = output.splitlines()
    for ind, line in enumerate(reversed_list):
        if line.lstrip().startswith('Score:'):
            point_breakdown = reversed_list[ind+1:][::-1]
            score_lines = reversed_list[:ind+1][::-1]
            break
    for line in score_lines:
        line = line.lstrip()
        if line.startswith('Total:'):
            _, score = line.rsplit(maxsplit=1)
    try:
        lines, score_f = '\n'.join(point_breakdown), float(score)
    except UnboundLocalError as e:
        print("No lines found with Score Tag?", e)
        raise e

    return lines, score_f

def main():
    parser = argparse.ArgumentParser(description='Grade an assignment')
    parser.add_argument('infile', help='the ok dump to be parsed')
    parser.add_argument('category', choices=['lab', 'hw', 'proj', 'quiz', 'vitamin', 'generic'])
    parser.add_argument('deadline', type=valid_date,
                        help='date when the assignment was due')

    parser.add_argument("--full-cutoff", type=float,
                        help='required number of tests to earn full credit')
    parser.add_argument('--partial-cutoff', type=float,
                        help='required number of tests to earn partial credit')
    parser.add_argument('--max-score', type=float,
                        help='score received when getting full credit')

    args = parser.parse_args()

    try:
        from info import info
        submitted_at = datetime.strptime(info['timestamp'],
                                         '%Y-%m-%d %H:%M:%S.%f')
    except ImportError:
        info = None
        submitted_at = datetime.now()

    with open(args.infile) as infile:
        output = infile.read()

    point_breakdown, score = parse_ok_output(output)
    score, reason = adjust_score(
        score,
        args.category,
        submitted_at,
        args.deadline,
        args.full_cutoff,
        args.partial_cutoff,
        args.max_score
    )
    print(point_breakdown, end='')
    print()
    if reason:
        print(reason)
        print()
    if args.category == 'proj':
        print('This score is for correctness only and does not include your composition score.')
        print()
    print('Score:')
    print('    Total:', score)

if __name__ == "__main__":
    main()
