#!/usr/bin/env pypy3

""" Christoph Dürr, Nadia Brauner Vettier - 2023
Graphistan - Poursuite - version 3

On nous donne un graphe G=(V,E). Supposons que G soit augmenté par des
auto-boucles pour tenir compte du fait que les joueurs peuvent rester sur
place. Notons G(u) l'ensemble des voisins d'un sommet u.

Modélisons le jeu sur un graphe orienté H. Les sommets de H sont composés d'un
couple de sommets (occupés par Henri et respectivement le tueur) et d'un bit
indiquant à qui le tour (HENRI ou KILLER).

D'une configuration (h, k, HENRI), il y a un arc vers toutes les
configurations de la forme (h1, k, KILLER) pour h1 voisin de h dans G.

D'une configuration (h, k, KILLER), il y a un arc vers toutes les
configurations de la forme (h, k1, HENRI) pour k1 voisin de k dans G.

Désormais les configurations sont étiquetées gagnantes ou perdantes de la
manière suivante, par simple propagation. Une configuration est gagnante si
le joueur qui commence en cette configuration peut gagner, et perdante s'il
ne peut pas gagner (en supposant que l'autre joueur joue parfaitement).

(1) Une configuration (h, h, HENRI) est perdante.

(2) Une configuration (h, k, t) est perdante si elle ne mène que vers des
configurations gagnants.

(3) Une configuration (h, k, t) est gagnante si elle mène vers au moins une
configuration perdante.

Initialement toutes les configurations sont sans étiquettes, sauf ceux qui
correspondent à la règle (1). Puis les règles (2) et (3) sont appliquées
jusqu'à obtenir un point fixe.

Concrètement ceci est calculé par un algorithme de propagation, utilisant une
pile de configurations qui viennent d'obtenir une étiquette (initialement ceux
qui correspondent à la règle (1)). Pour chaque configuration c il y a
également un compteur nb_escape[c], indiquant le nombre de configurations
non-gagnants menant vers c. Dés que nb_escape[c] devient zéro, on pose label
[c]=LOOSING et c rejoint la pile.

Les sommets h tel qu'il n'existe pas de k avec (h, k, HENRI) perdant sont
exactement les sommets sûrs.

"""

from random import randint, shuffle, seed 
from typing import Iterator
import sys

def readints(): return map(int, sys.stdin.readline().strip().split())

def add_edge(G, u, v):
	G[u].add(v)
	G[v].add(u)


def read_graph():
	""" every edge (u,v) generates a line of the form 'e' u v.
	Vertex indices are zero-based.
	"""
	n, m = readints()
	G = [{u} for u in range(n)]
	for _ in range(m):
		u, v = readints()
		add_edge(G, u, v)
	return G 

HENRI = 0
KILLER = 1
LOOSING = 0
WINNING = 1
FORWARD = 0
BACKWARD = 1

def move(config, G, direction):
	""" Iterator over configurations reached by given config
	in one move. 
	"""
	h, k, turn = config
	if turn == direction:
		for h1 in G[h]:
			yield(h1, k, 1 - turn)
	else:
		for k1 in G[k]:
			yield(h, k1, 1 - turn)

def configurations(G) -> Iterator[tuple[int, int, int]]:
	V = range(len(G))
	for h in V:
		for k in V:
			for t in (HENRI, KILLER):
				yield (h, k, t)


def solve(G: list[set[int]]) -> list[int]:
	"""	
	We assume that self loops have been added to G.
	Complexity: O(V^2 d)
	Explanation: O(V^2) configurations in Q. 
	For each there is a loop on k1, leading to O(V^2 d) time.
	When killer wins on a config, (which happens O(V^2) times), 
	there is a loop on h1, leading to O(V^2 d) time again.
	"""
	V = range(len(G))
	# invariant: nb_escapes[c] is the number of non-winning configurations reached from c
	nb_escapes = {c: len(list(move(c, G, FORWARD))) for c in configurations(G)}
	label = {(v, v, HENRI): LOOSING for v in V}
	to_process = list(label.keys()) # contains freshly labeled configurations
	while to_process:
		config = to_process.pop()
		if label[config] == LOOSING:
			for c1 in move(config, G, BACKWARD):
				if c1 not in label:
					label[c1] = WINNING
					to_process.append(c1)
		elif label[config] == WINNING:
			for c1 in move(config, G, BACKWARD):
				nb_escapes[c1] -= 1
				if nb_escapes[c1] == 0 and c1 not in label:
					label[c1] = LOOSING
					to_process.append(c1)
	safe = []
	for h in V:
		is_safe = True
		for k in V:
			if k != h:
				config = (h, k, HENRI)
				if config in label and label[config] == LOOSING:
					is_safe = False 
		if is_safe:
			safe.append(h)
	return safe


def generate() -> None:
    """ Generates the union of
    - a circle. All vertices are safe. Vertices in range(0, m)
    - A path. No vertex is safe.  Vertices in range(m, 2*m)
    - A random graph (not the usual model), some vertices are safe.  Vertices in range(2*m, 3*m)
    All vertex indices are randomly shuffled.
    """
    m = 333
    d = 10
    n = 3 * m 
    G = [set() for u in range(n)]
    label = list(range(n))
    shuffle(label)
    # add circle
    for u in range(m):
        add_edge(G, label[u], label[((u + 1) % m)])
    # add path
    for u in range(m - 1):
        add_edge(G, label[m + u], label[m + u + 1])
    # add random graph
    for _ in range(m * d):
        u = randint(0, m - 1)
        v = randint(u, u + d ) % m 
        u1 = label[2*m + u]
        v1 = label[2*m + v]
        if u1 != v1 and len(G[u1]) < 3 * d and len(G[v1]) < 3 * d:
            add_edge(G, u1, v1) 
    # count number of edges
    edges = sum(len(Gu) for Gu in G) // 2 
    print(n, edges)
    for u, Gu in enumerate(G):
        for v in Gu:
            if u < v:
                print(u, v)


def print_sol(safe):
	# print("sum is", sum(safe))
	print(sum(safe))
	print("actual vertices are", safe, file=sys.stderr)
	print("number of safe vertices is", len(safe), file=sys.stderr)


if __name__ == "__main__":

	if len(sys.argv) == 1:
		print_sol(solve(read_graph()))
	else:
		seed(int(sys.argv[1]))
		generate()
