# THIS IS TAKEN FROM THE LAB 6 CODE, WITH A SLIGHT MODIFICATION SO THAT WE CAN CHOOSE THE RANDOM SEED IN THE BETA DISTRIBUTION

from scipy import stats
import matplotlib.pyplot as plt
import numpy as np


def alphaBetaFromAmB(a: int, m: int, b: int):
    # Taken from code by David L. Mueller
    #github dlmueller/PERT-Beta-Python
    first_numer_alpha = 2.0 * (b + 4 * m - 5 * a)
    first_numer_beta = 2.0 * (5 * b - 4 * m - a)
    first_denom = 3.0 * (b - a)
    second_numer = (m - a) * (b - m)
    second_denom = (b - a) ** 2
    second = (1 + 4 * (second_numer / second_denom))
    alpha = (first_numer_alpha / first_denom) * second
    beta = (first_numer_beta / first_denom) * second
    return alpha, beta


def generateTaskTime(a: int, m: int, b: int, seed: int = 42):
    
    alpha, beta = alphaBetaFromAmB(a, m, b)
    location = a
    scale = b - a
    
    taskTime = stats.beta.rvs(alpha, beta) * scale + location
    
    return taskTime


# Script to evaluate a project
if __name__ == "__main__":    
    CompletionTimes = [0]*1000
    ExpectedTimes = [0]*1000

    for i in range(len(CompletionTimes)):
        # Calculate task times
        A = generateTaskTime(3,7,8)
        B = generateTaskTime(2,4,6)
        C = generateTaskTime(1,3,7)
        D = generateTaskTime(1,4,6)
        E = generateTaskTime(2,5,6)
        F = generateTaskTime(4,6,9)
        G = generateTaskTime(2,6,11)
        H = generateTaskTime(4,5,6)
        I = generateTaskTime(2,4,6)
        J = generateTaskTime(1,2,3)
            
        # Calculate times of all paths
        Path1 = B + D + E + F + I + J # Critical path
        Path2 = A + E + F + I + J
        Path3 = C + E + F + I + J
        Path4 = A + E +  H + I + J
        Path5 = B + D + E + H + I + J
        Path6 = C + G + H + I + J

        
        ExpectedTimes[i] = Path1
        CompletionTimes[i] = max(Path1, Path2, Path3, Path4, Path5, Path6)

    # Histograms
    plt.hist(CompletionTimes, density=True, histtype='stepfilled', alpha=0.2)
    plt.show()

    plt.hist(ExpectedTimes, density=True, histtype='stepfilled', alpha=0.2)
    plt.show()
    # Average completion time
    print(np.mean(CompletionTimes))

    # One sample t-test, with H0 = expected completion time.
    print(stats.ttest_1samp(CompletionTimes, 31))

    # Percentile interval
    CompletionTimes.sort()
    print(CompletionTimes[25])
    print(CompletionTimes[975])

    # Error rate`
    print(sum(np.greater(CompletionTimes, ExpectedTimes))/len(CompletionTimes))