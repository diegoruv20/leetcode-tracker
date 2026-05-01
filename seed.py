"""Seed the database with LeetCode 75 problems."""
from app import create_app
from models import db, Category, Topic, Problem, ProblemTopic

TOPICS_LIST = [
    "Array / String", "Two Pointers", "Sliding Window", "Prefix Sum",
    "Hash Map / Set", "Stack", "Queue", "Linked List", "Binary Tree - DFS",
    "Binary Tree - BFS", "Binary Search Tree", "Graph - DFS", "Graph - BFS",
    "Heap / Priority Queue", "Binary Search", "Backtracking", "DP - 1D",
    "DP - Multidimensional", "Bit Manipulation", "Trie", "Intervals",
    "Monotonic Stack", "Math",
]

# (name, leetcode_url_slug, difficulty, [topics])
LEETCODE_75 = [
    # Array / String
    ("Merge Strings Alternately", "merge-strings-alternately", "Easy", ["Array / String"]),
    ("Greatest Common Divisor of Strings", "greatest-common-divisor-of-strings", "Easy", ["Array / String", "Math"]),
    ("Kids With the Greatest Number of Candies", "kids-with-the-greatest-number-of-candies", "Easy", ["Array / String"]),
    ("Can Place Flowers", "can-place-flowers", "Easy", ["Array / String"]),
    ("Reverse Vowels of a String", "reverse-vowels-of-a-string", "Easy", ["Array / String", "Two Pointers"]),
    ("Reverse Words in a String", "reverse-words-in-a-string", "Medium", ["Array / String"]),
    ("Product of Array Except Self", "product-of-array-except-self", "Medium", ["Array / String", "Prefix Sum"]),
    ("Increasing Triplet Subsequence", "increasing-triplet-subsequence", "Medium", ["Array / String"]),
    ("String Compression", "string-compression", "Medium", ["Array / String", "Two Pointers"]),
    # Two Pointers
    ("Move Zeroes", "move-zeroes", "Easy", ["Two Pointers", "Array / String"]),
    ("Is Subsequence", "is-subsequence", "Easy", ["Two Pointers"]),
    ("Container With Most Water", "container-with-most-water", "Medium", ["Two Pointers"]),
    ("Max Number of K-Sum Pairs", "max-number-of-k-sum-pairs", "Medium", ["Two Pointers", "Hash Map / Set"]),
    # Sliding Window
    ("Maximum Average Subarray I", "maximum-average-subarray-i", "Easy", ["Sliding Window"]),
    ("Maximum Number of Vowels in a Substring of Given Length", "maximum-number-of-vowels-in-a-substring-of-given-length", "Medium", ["Sliding Window"]),
    ("Max Consecutive Ones III", "max-consecutive-ones-iii", "Medium", ["Sliding Window"]),
    ("Longest Subarray of 1's After Deleting One Element", "longest-subarray-of-1s-after-deleting-one-element", "Medium", ["Sliding Window"]),
    # Prefix Sum
    ("Find the Highest Altitude", "find-the-highest-altitude", "Easy", ["Prefix Sum"]),
    ("Find Pivot Index", "find-pivot-index", "Easy", ["Prefix Sum"]),
    # Hash Map / Set
    ("Find the Difference of Two Arrays", "find-the-difference-of-two-arrays", "Easy", ["Hash Map / Set"]),
    ("Unique Number of Occurrences", "unique-number-of-occurrences", "Easy", ["Hash Map / Set"]),
    ("Determine if Two Strings Are Close", "determine-if-two-strings-are-close", "Medium", ["Hash Map / Set"]),
    ("Equal Row and Column Pairs", "equal-row-and-column-pairs", "Medium", ["Hash Map / Set"]),
    # Stack
    ("Removing Stars From a String", "removing-stars-from-a-string", "Medium", ["Stack"]),
    ("Asteroid Collision", "asteroid-collision", "Medium", ["Stack"]),
    ("Decode String", "decode-string", "Medium", ["Stack"]),
    # Queue
    ("Number of Recent Calls", "number-of-recent-calls", "Easy", ["Queue"]),
    ("Dota2 Senate", "dota2-senate", "Medium", ["Queue"]),
    # Linked List
    ("Delete the Middle Node of a Linked List", "delete-the-middle-node-of-a-linked-list", "Medium", ["Linked List"]),
    ("Odd Even Linked List", "odd-even-linked-list", "Medium", ["Linked List"]),
    ("Reverse Linked List", "reverse-linked-list", "Easy", ["Linked List"]),
    ("Maximum Twin Sum of a Linked List", "maximum-twin-sum-of-a-linked-list", "Medium", ["Linked List", "Two Pointers"]),
    # Binary Tree - DFS
    ("Maximum Depth of Binary Tree", "maximum-depth-of-binary-tree", "Easy", ["Binary Tree - DFS"]),
    ("Leaf-Similar Trees", "leaf-similar-trees", "Easy", ["Binary Tree - DFS"]),
    ("Count Good Nodes in Binary Tree", "count-good-nodes-in-binary-tree", "Medium", ["Binary Tree - DFS"]),
    ("Path Sum III", "path-sum-iii", "Medium", ["Binary Tree - DFS", "Prefix Sum"]),
    ("Longest ZigZag Path in a Binary Tree", "longest-zigzag-path-in-a-binary-tree", "Medium", ["Binary Tree - DFS"]),
    ("Lowest Common Ancestor of a Binary Tree", "lowest-common-ancestor-of-a-binary-tree", "Medium", ["Binary Tree - DFS"]),
    # Binary Tree - BFS
    ("Binary Tree Right Side View", "binary-tree-right-side-view", "Medium", ["Binary Tree - BFS"]),
    ("Maximum Level Sum of a Binary Tree", "maximum-level-sum-of-a-binary-tree", "Medium", ["Binary Tree - BFS"]),
    # Binary Search Tree
    ("Search in a Binary Search Tree", "search-in-a-binary-search-tree", "Easy", ["Binary Search Tree"]),
    ("Delete Node in a BST", "delete-node-in-a-bst", "Medium", ["Binary Search Tree"]),
    # Graph - DFS
    ("Keys and Rooms", "keys-and-rooms", "Medium", ["Graph - DFS"]),
    ("Number of Provinces", "number-of-provinces", "Medium", ["Graph - DFS"]),
    ("Reorder Routes to Make All Paths Lead to the City Zero", "reorder-routes-to-make-all-paths-lead-to-the-city-zero", "Medium", ["Graph - DFS"]),
    ("Evaluate Division", "evaluate-division", "Medium", ["Graph - DFS"]),
    # Graph - BFS
    ("Nearest Exit from Entrance in Maze", "nearest-exit-from-entrance-in-maze", "Medium", ["Graph - BFS"]),
    ("Rotting Oranges", "rotting-oranges", "Medium", ["Graph - BFS"]),
    # Heap / Priority Queue
    ("Kth Largest Element in an Array", "kth-largest-element-in-an-array", "Medium", ["Heap / Priority Queue"]),
    ("Smallest Number in Infinite Set", "smallest-number-in-infinite-set", "Medium", ["Heap / Priority Queue"]),
    ("Maximum Subsequence Score", "maximum-subsequence-score", "Medium", ["Heap / Priority Queue"]),
    ("Total Cost to Hire K Workers", "total-cost-to-hire-k-workers", "Medium", ["Heap / Priority Queue"]),
    # Binary Search
    ("Guess Number Higher or Lower", "guess-number-higher-or-lower", "Easy", ["Binary Search"]),
    ("Successful Pairs of Spells and Potions", "successful-pairs-of-spells-and-potions", "Medium", ["Binary Search"]),
    ("Find Peak Element", "find-peak-element", "Medium", ["Binary Search"]),
    ("Koko Eating Bananas", "koko-eating-bananas", "Medium", ["Binary Search"]),
    # Backtracking
    ("Letter Combinations of a Phone Number", "letter-combinations-of-a-phone-number", "Medium", ["Backtracking"]),
    ("Combination Sum III", "combination-sum-iii", "Medium", ["Backtracking"]),
    # DP - 1D
    ("N-th Tribonacci Number", "n-th-tribonacci-number", "Easy", ["DP - 1D"]),
    ("Min Cost Climbing Stairs", "min-cost-climbing-stairs", "Easy", ["DP - 1D"]),
    ("House Robber", "house-robber", "Medium", ["DP - 1D"]),
    ("Domino and Tromino Tiling", "domino-and-tromino-tiling", "Medium", ["DP - 1D"]),
    # DP - Multidimensional
    ("Unique Paths", "unique-paths", "Medium", ["DP - Multidimensional"]),
    ("Longest Common Subsequence", "longest-common-subsequence", "Medium", ["DP - Multidimensional"]),
    ("Best Time to Buy and Sell Stock with Transaction Fee", "best-time-to-buy-and-sell-stock-with-transaction-fee", "Medium", ["DP - Multidimensional"]),
    ("Edit Distance", "edit-distance", "Medium", ["DP - Multidimensional"]),
    # Bit Manipulation
    ("Counting Bits", "counting-bits", "Easy", ["Bit Manipulation"]),
    ("Single Number", "single-number", "Easy", ["Bit Manipulation"]),
    ("Minimum Flips to Make a OR b Equal to c", "minimum-flips-to-make-a-or-b-equal-to-c", "Medium", ["Bit Manipulation"]),
    # Trie
    ("Implement Trie (Prefix Tree)", "implement-trie-prefix-tree", "Medium", ["Trie"]),
    ("Search Suggestions System", "search-suggestions-system", "Medium", ["Trie"]),
    # Intervals
    ("Non-overlapping Intervals", "non-overlapping-intervals", "Medium", ["Intervals"]),
    ("Minimum Number of Arrows to Burst Balloons", "minimum-number-of-arrows-to-burst-balloons", "Medium", ["Intervals"]),
    # Monotonic Stack
    ("Daily Temperatures", "daily-temperatures", "Medium", ["Monotonic Stack"]),
    ("Online Stock Span", "online-stock-span", "Medium", ["Monotonic Stack"]),
]


def seed():
    app = create_app()
    with app.app_context():
        if Problem.query.count() > 0:
            print("Database already seeded. Skipping.")
            return

        # Create category
        cat = Category(name="LeetCode 75")
        db.session.add(cat)
        db.session.flush()

        # Create topics
        topic_map = {}
        for name in TOPICS_LIST:
            t = Topic(name=name)
            db.session.add(t)
            db.session.flush()
            topic_map[name] = t

        # Create problems
        for name, slug, difficulty, topic_names in LEETCODE_75:
            p = Problem(
                name=name,
                url=f"https://leetcode.com/problems/{slug}/",
                difficulty=difficulty,
                category_id=cat.id,
                leitner_box=1,
            )
            for tn in topic_names:
                p.topics.append(topic_map[tn])
            db.session.add(p)

        db.session.commit()
        print(f"Seeded {len(LEETCODE_75)} problems across {len(TOPICS_LIST)} topics.")


if __name__ == "__main__":
    seed()
