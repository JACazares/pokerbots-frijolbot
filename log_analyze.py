import re
import matplotlib.pyplot as plt

def read_gamelog(filename):
    with open(filename) as f:
        raw_data = f.readlines()
    
    scoresA = []
    scoresB = []
    for line in raw_data:
        lineAB = re.match("Round #[0-9]*, A \((-?[0-9]*)\), B \((-?[0-9]*)\)", line)
        lineBA = re.match("Round #[0-9]*, B \((-?[0-9]*)\), A \((-?[0-9]*)\)", line)
        if lineAB:
            scoresA.append(int(lineAB.group(1)))
            scoresB.append(int(lineAB.group(2)))
        elif lineBA:
            scoresA.append(int(lineBA.group(2)))
            scoresB.append(int(lineBA.group(1)))
        else:
            finalLine = re.match("Final, A \((-?[0-9]*)\), B \((-?[0-9]*)\)", line)
            if finalLine:
                scoresA.append(int(finalLine.group(1)))
                scoresB.append(int(finalLine.group(2)))
    
    return (scoresA, scoresB)

if __name__ == "__main__":
    scoreA, scoreB = read_gamelog("gamelog.txt")
    print(f"Final, A ({scoreA[-1]}), B ({scoreB[-1]})")
    delta = [scoreA[i] - scoreA[i - 1] for i in range(1, len(scoreA))]

    plt.title("Player A")
    plt.plot(list(range(1, len(scoreA)+1)), scoreA, marker='o', linestyle='-', markersize=2, color="red")
    plt.plot(list(range(1, len(delta)+1)), delta, marker='o', linestyle='-', markersize=2, color="blue")
    #plt.plot(list(range(1, len(scoreB)+1)), scoreB, marker='o', linestyle='-', markersize=2, color="blue")
    plt.show()
    pass