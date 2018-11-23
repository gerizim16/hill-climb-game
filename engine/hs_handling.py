def get_highscores(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as hs_file:
            highscores = list()
            line = hs_file.readline()
            while line:
                name, score = line.rstrip('\n').split(',')
                highscores.append((name, float(score)))
                line = hs_file.readline()
        return tuple(highscores)
    except FileNotFoundError:
        return None

def add_highscore(filename, name, score, ascending=True):
    current_hs = get_highscores(filename)
    if current_hs: # highscore found
        current_hs = list(current_hs)
        current_hs.append((name, score))
        print(current_hs)
        current_hs = sorted(current_hs, 
                            key=lambda item: item[1], reverse=not ascending)
        current_hs = current_hs[0:50-1] # only store top 50
    else: # no highscore yet
        current_hs = ((name, score),)
    with open(filename, 'w', encoding='utf-8') as hs_file:
        for highscore in current_hs:
            name, score = highscore
            hs_file.write('{},{}\n'.format(name, score))
