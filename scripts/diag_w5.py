import json, sys
r = json.loads(open(sys.argv[1], encoding='utf-8').read())['sweep']['grid']
for row in r:
    for c in row:
        print(f"gamma={c['gamma']:.3f} delta={c['delta']:.2f} emp={c['empirical_mean']:6.1f} theory={c['theoretical_lb']:8.1f}")
