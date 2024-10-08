import openai
import pandas as pd
import time
import logging
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(filename='processing_log.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

# Function to handle each  prompt
def get_response(prompt, max_runtime=20, retries=3):
    print(f"Sending prompt: {prompt}")  # Debugging line
    for attempt in range(retries):
        try:
            # Start measuring time
            start_time = time.time()
            
            # Use a thread pool for timeout handling
            with ThreadPoolExecutor() as executor:
                future = executor.submit(openai.ChatCompletion.create, 
                                         model="gpt-3.5-turbo", 
                                         messages=[{"role": "user", "content": prompt}],
                                         temperature=0)
                response = future.result(timeout=max_runtime)
            
            # Measure end time
            end_time = time.time()
            
            # Calculate runtime
            runtime = end_time - start_time
            
            print(f"Received response in {runtime} seconds")  
            return response.choices[0].message['content'], runtime

        except TimeoutError:
            logging.error(f"Timeout occurred for prompt: {prompt}, attempt {attempt + 1}/{retries}")
            if attempt + 1 == retries:
                return None, None  # If max retries reached, return None

        except openai.error.OpenAIError as e:
            logging.error(f"OpenAI API error for prompt: {prompt} - {str(e)}")
            return None, None  

        except Exception as e:
            logging.error(f"Unexpected error for prompt: {prompt} - {str(e)}")
            return None, None  


# Function to process each problem
def process_problem(problem, max_runtime=35, retries=3):
    # Initial prompt
    initial_prompt = problem['initial_prompt'] + " Please do not show any steps; just provide the final solution."
    initial_response, initial_runtime = get_response(initial_prompt, max_runtime, retries)
    
    # Skip if error in response
    if initial_response is None:
        return None
    
    if problem.get('type') == 'logic':
        modified_prompt = problem['initial_prompt'] + " Show me your logical steps and reasoning to solve this puzzle. Logic can be tricky, so pay close attention to avoid any traps."
    else:
        modified_prompt = problem['initial_prompt'] + " Show me your steps to the solution. Carefully think through this step-by-step till you reach the end needed answer."

    modified_response, modified_runtime = get_response(modified_prompt, max_runtime, retries)
    
    # Skip if error
    if modified_response is None:
        return None
    
    # Return results as a dictionary
    return {
        "problem_id": problem['id'],
        "initial_prompt": initial_prompt,
        "initial_response": initial_response,
        "initial_runtime": initial_runtime,
        "modified_prompt": modified_prompt,
        "modified_response": modified_response,
        "modified_runtime": modified_runtime
    }


# Function to process batch using ThreadPoolExecutor
def process_batch(batch, batch_number, max_runtime=20, retries=3, max_workers=5):
    results = []
    
    # Use ThreadPoolExecutor for parallelism
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all problems to the executor
        futures = [executor.submit(process_problem, problem, max_runtime, retries) for problem in batch]

        # Collect results as they complete
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    results.sort(key=lambda x: x['problem_id'])

    
    # Save results
    df = pd.DataFrame(results)
    df.to_csv(f"random_selects_clarification{16}.csv", index=False)

    # Print results
    for result in results:
        print(f"Problem ID: {result['problem_id']}")
        print(f"Initial Prompt: {result['initial_prompt']}")
        print(f"Initial Response: {result['initial_response']}")
        print(f"Initial Runtime: {result['initial_runtime']} seconds")
        print(f"Modified Prompt: {result['modified_prompt']}")
        print(f"Modified Response: {result['modified_response']}")
        print(f"Modified Runtime: {result['modified_runtime']} seconds")
        print("\n")
        


# Example batch of problems
batch_16 = [
    {"id": 6, "initial_prompt": "Wie groß ist die Summe aller fünfstelligen Zahlen, die man aus den Ziffern 1, 2, 3, 4 und 5 bilden kann? Jede Ziffer darf in jeder Zahl nur einmal verwendet werden."},
    {"id": 8, "initial_prompt": "Um wie viel ist die Summe der ungeraden sechsstelligen Zahlen größer als die Summe der geraden sechsstelligen Zahlen?"},
    {"id": 18, "initial_prompt": "Bestimme alle natürlichen Zahlen n, für die n^5 n durch 120 teilbar ist."},
    {"id": 20, "initial_prompt": "Gesucht sind alle Brüche mit dem Wert 2/5, bei denen die Summe aus Zähler und Nenner eine Quadratzahl mit höchstens drei Ziffern ist."},
    {"id": 26, "initial_prompt": "Die quadratische Gleichung x^2 + ax + a - 2 = 0 besitze die Lösungen x1 und x2. Für welchen Parameterwert a nimmt die Summe der Quadrate von x1 und x2 den kleinsten Wert an?"},
    {"id": 27, "initial_prompt": "Für welche Werte von a und b ist x^2 + 5x + 6 ein Teiler von x^4 + ax^3 - x^2 + ax + b?"},
    {"id": 32, "initial_prompt": "Wie viele dreistellige Zahlen abc gibt es, bei denen die Summe von zwei Ziffern gleich der verbleibenden Ziffer ist? (Beispiel: 473, denn 4 + 3 = 7 ). Erwartet wird keine Aufzählung dieser Zahlen, sondern die Bestimmung der Anzahl mit Begründung."},
    {"id": 37, "initial_prompt": "Wie viele sechsstellige Zahlen, in denen jede der Ziffern 1, 2, 3, 4, 5 und 6 genau einmal vorkommt, sind durch 3 aber nicht durch 9 und durch 4 aber nicht durch 8 teilbar?"},
    {"id": 42, "initial_prompt": """Turnip for the books:  ‘It’s been a good year for turnips,’ farmer Hogswill remarked to his neighbour, Farmer Suticle.
‘Yup, that it has,’ the other replied. ‘How many did you grow?’
‘Well . . . I don’t exactly recall, but I do remember that when I took the turnips to market, I sold six-sevenths of them, plus one-seventh of a turnip, in the first hour.’
‘Must’ve been tricky cuttin’ ’em up.’
‘No, it was a whole number that I sold. I never cuts ’em.’ ‘If’n you say so, Hogswill. Then what?’
‘I sold six-sevenths of what was left, plus one-seventh of a
turnip, in the second hour. Then I sold six-sevenths of what was left, plus one-seventh of a turnip, in the third hour. And finally I sold six-sevenths of what was left, plus one-seventh of a turnip, in the fourth hour. Then I went home.’
‘Why?’
‘’Cos I’d sold the lot.’
How many turnips did Hogswill take to market?
"""},

    {"id": 60, "initial_prompt": """Hippopotamian Logic
I won’t eat my hat.
If hippos don’t eat acorns, then oak trees will grow in Africa.
If oak trees don’t grow in Africa, then squirrels hibernate in winter.
If hippos eat acorns and squirrels hibernate in winter, then I’ll eat my hat.
Therefore – what?
"""},

    {"id": 79, "initial_prompt": "Ein Erfinder stellt drei Maßnahmen vor, die jeweils den Energieverbrauch eines Motors reduzieren sollen. Die erste verringert den Verbrauch um 20%, die zweite um 30% und die dritte gar um 50%. Kann der Verbrauch des Motors mit allen drei auf null reduziert werden? Wenn nein, auf wie viel dann?"},
    {"id": 81, "initial_prompt": r"""Berechnen Sie zu den komplexen Zahlen
\[ z_1 = 1 - i, \quad z_2 = 1 + 3i, \quad z_3 = 2 - 4i \]

die Real- und Imaginärteile der Ausdrücke
1. \(-z_1\)
2. \( \overline{z_1} \) (conjugate of \( z_1 \))
3. \( z_1 z_2 \) (product of \( z_1 \) and \( z_2 \))
4. \( \frac{z_2}{z_3} \) (quotient of \( z_2 \) by \( z_3 \))
5. \( \frac{z_1}{\overline{z_2} - z_1^2} \)
6. \( \frac{z_3}{2z_1 - \overline{z_2}} \) 
"""},
    {"id": 88, "initial_prompt": "Ist ein reelles lineares Gleichungssystem (A|B) mit n Unbekannten und n Gleichungen für ein b eindeutig lösbar, so ist es dies auch für jedes b - stimmt das?"},
    {"id": 95, "initial_prompt": "Von einer Fußballmannschaft (11 Mann) sind 4 Spieler jünger als 25 Jahre, 3 sind 25, der Rest (4 Spieler) ist älter. Das Durchschnittsalter liegt bei 28 Jahren. Wo liegt der Median? Wie ändern sich Median und Mittelwert, wenn für den 40-jährigen Torwart ein 18-jähriger eingewechselt wird?"},
    {"id": 97, "initial_prompt": "„Wenn zwei Merkmale X und Y stark miteinander korrelieren, dann muss eine kausale Beziehung zwischen X und Y herrschen.“ Ist diese Aussage richtig?"},
    {"id": 101, "initial_prompt": "Ein Autokennzeichen bestehe aus 1 bis 3 Buchstaben gefolgt von 4 Ziffern. Wie viel verschiedene Kennzeichen können so erzeugt werden?"},
    {"id": 119, "initial_prompt": r"""Bestimmen Sie Real- und Imaginärteil der Lösungen folgende quadratische Gleichung
\( (z-(1+2 \mathrm{i})) z=3-\mathrm{i} \)
"""},

    {"id": 123, "initial_prompt": r"""\( \cdot \) Für welche Startwerte \( a_{0} \in \mathbb{R} \) konvergiert die rekursiv definierte Folge \( \left(a_{n}\right) \) mit
\[
a_{n+1}=\frac{1}{4}\left(a_{n}^{2}+3\right), \quad n \in \mathbb{N} \text { ? }
\]
""" },

    {"id": 132, "initial_prompt": r"""Bestimmen Sie den Konvergenzradius und den Konvergenzkreis der folgenden Potenzreihen.
\( \left(\sum_{n=0}^{\infty} \frac{n+\mathrm{i}}{(\sqrt{2} \mathrm{i})^{n}}\binom{2 n}{n} z^{2 n}\right) \)
"""},

    {"id": 133, "initial_prompt": r"""Bestimmen Sie den Konvergenzradius und den Konvergenzkreis der folgenden Potenzreihen.
\( \left(\sum_{n=0}^{\infty} \frac{(2+\mathrm{i})^{n}-\mathrm{i}}{\mathrm{i}^{n}}(z+\mathrm{i})^{n}\right) \)
"""},

    {"id": 140, "initial_prompt": r"""Man bestimme die im Folgenden angegebenen Integrale:
\[
I=\int x \sin x \mathrm{~d} x
\]
"""},

    {"id": 142, "initial_prompt": r""" \[
I_{1}=\int \frac{x}{\cosh ^{2} x} \mathrm{~d} x, \quad I_{2}=\int \frac{\ln \left(x^{2}\right)}{x^{2}} \mathrm{~d} x
\]
"""},

    {"id": 145, "initial_prompt": r"""\[
I=\int \cos \left(\mathrm{e}^{\sin x}\right) \mathrm{e}^{\sin x} \cos x \mathrm{~d} x
\]
 """},

    {"id": 151, "initial_prompt": r""""Bestimmen Sie die allgemeine Lösung der linearen Differenzialgleichung erster Ordnung
\[
u^{\prime}(x)+\cos (x) u(x)=\frac{1}{2} \sin (2 x), \quad x \in(0, \pi) \text {. }
\]
"""},

    {"id": 158, "initial_prompt": r"""Berechnen Sie die Determinanten der folgenden reellen Matrizen:
\[
\mathbf{A}=\left(\begin{array}{llll}
1 & 2 & 0 & 0 \\
2 & 1 & 0 & 0 \\
0 & 0 & 3 & 4 \\
0 & 0 & 4 & 3
\end{array}\right)
"""},

    {"id": 159, "initial_prompt": r"""Berechnen Sie die Determinanten der folgenden reellen Matrizen:
\quad \mathbf{B}=\left(\begin{array}{lllll}
2 & 0 & 0 & 0 & 2 \\
0 & 2 & 0 & 2 & 0 \\
0 & 0 & 2 & 0 & 0 \\
0 & 2 & 0 & 2 & 0 \\
2 & 0 & 0 & 0 & 2
\end{array}\right)
\]
"""},

    {"id": 160, "initial_prompt": r"""Geben Sie die Eigenwerte und Eigenvektoren der folgenden Matrix an:
\( \mathbf{A}=\left(\begin{array}{cc}3 & -1 \\ 1 & 1\end{array}\right) \in \mathbb{R}^{2 \times 2} \)
"""},

    {"id": 173, "initial_prompt": r"""Bestimmen Sie alle kritischen Punkte der folgenden Differenzialgleichungssysteme.
(a)
\[
\begin{array}{l}
x_{1}^{\prime}(t)=x_{1}(t)+\left(x_{2}(t)\right)^{2} \\
x_{2}^{\prime}(t)=x_{1}(t)+x_{2}(t)
\end{array}
\]
"""},

    {"id": 184, "initial_prompt": "1+3+2+1+4+6+7+8+9+9+5+4-7+2=?"},
    {"id": 190, "initial_prompt": "A hotel comprises 67 floors above ground and 4 floors below ground. A guest parks on floor -3, in the basement, and is staying on the 43rd floor of the hotel. How many floors must he go up to get from his car to his hotel room?"},
    {"id": 197, "initial_prompt": "A person walks along a beach, starting at point A, at a rate of 3 mi/h and at point B, goes into the water and swims at a rate of 2 mi/h diagonally out to an island that is a distance of √3 miles from point C, directly across from the island on the shore, as shown in the picture. The total distance from point A to point C is 3 miles. There are two different choices for the distance, in miles, from point A to point B that will result in a total time for walking and swimming of one hour and 40 minutes; what is the sum of those numbers?"}, 
    {"id": 204, "initial_prompt": """ Three of the robots, all from different models, have missing model IDs: 
- Rae is not the newest. 
- Knuck is the oldest. 
- Lex is not the oldest.
 What's the correct order from the newest to the oldest?
"""},

    {"id": 205, "initial_prompt": "Susan and Lisa decided to play tennis against each other. They bet $1 on each game they played. Susan won three bets and Lisa won $5. How many games did they play?"},
    {"id": 208, "initial_prompt": "A girl meets a lion and unicorn in the forest. The lion lies every Monday, Tuesday and Wednesday and the other days he speaks the truth. The unicorn lies on Thursdays, Fridays and Saturdays, and the other days of the week he speaks the truth. “Yesterday I was lying,” the lion told the girl. “So was I,” said the unicorn. What day is it?"},
    {"id": 209, "initial_prompt": """ All knights are brave.
All skilled people have done practice.
Therefore, some knights have done
practice.

 Is this argument valid?
"""}
]


process_batch(batch_16, 16, max_runtime=35, retries=3, max_workers=10)  


