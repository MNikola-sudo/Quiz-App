from flask import Flask, render_template, request, redirect, url_for, flash, session
import random
import sqlite3 as sql
from pitanja import kviz_pitanja


baza='nova_baza.db'
konekcija=sql.connect(baza)


app = Flask(__name__)
app.secret_key ='12345678' 

@app.route('/')

@app.route('/kvizstart',methods=['GET', 'POST'])
def kvizstart():
    return render_template('kviz.html')

@app.route('/pocetna', methods=['POST', 'GET'])
def pocetna():
    if 'score' not in session:
        session['score'] = 0
    if 'iskoristena_lista' not in session:
        session['iskoristena_lista'] = []

    dostupna_lista = []
    score = session['score']
    iskoristena_lista = session['iskoristena_lista']

    for pitanje_id, pitanje_tekst in kviz_pitanja.items():
        if pitanje_id not in iskoristena_lista:
            dostupna_lista.append(pitanje_tekst)

    if dostupna_lista:
        nasumicno_pitanje = random.choice(dostupna_lista)
        for pit_id, pit_tekst in kviz_pitanja.items():
            if pit_tekst == nasumicno_pitanje:
                iskoristena_lista.append(pit_id)
                break

        odgovor = [odgovor for odgovor in nasumicno_pitanje["odgovori"]]
        tocan_odg = nasumicno_pitanje['tocan_odgovor']

        if request.method == 'POST':
            button_id = request.form.get("button_id")
            odg_id = request.form.get('odg_id')

            if button_id and odg_id:             
                button_id = button_id.strip()
                odg_id = odg_id.strip()

                if button_id[0] == odg_id:
                    flash(f'TOČNO: {odg_id}')
                    session['score'] += 5
                    session['iskoristena_lista'] = iskoristena_lista
                    return redirect(url_for('pocetna'))
                else:
                    if session['score'] > 40: # više od 40 bodova za upis u high score 
                        session['iskoristena_lista'] = iskoristena_lista
                        return render_template('dodaj_score.html',score=session['score'])

                    session['score'] = 0
                    flash(f'NETOČNO!!')
                    session['iskoristena_lista'] = iskoristena_lista
                    return redirect(url_for('score'))

            else:
                flash("Pojavila se greška..prilikom ucitavanja bodova..")
                return redirect(url_for('pocetna'))

    if not dostupna_lista:
        flash(f'Nema više pitanja!! Pobijedili ste! Ukupno osvojenih bodova: {score}')
        session['iskoristena_lista'] = []
        session['score'] = 0
        return render_template('kviz_play.html')

    return render_template('kviz_play.html', pitanje=nasumicno_pitanje['pitanje'], odgovor=odgovor, tocan_odg=tocan_odg, score=score)

@app.route('/dodaj_highscore',methods=['POST','GET'])
def dodaj_highscore():
    if request.method == 'POST':
        ime = request.form.get("ime")
        user_score = request.form.get('score')
        print(ime,user_score)
        if ime and user_score:
            konekcija=sql.connect(baza)
            kursor=konekcija.cursor()
            unos_querya = '''
                            INSERT INTO highscore (bodovi, ime) 
                            VALUES (?, ?);
                            '''
            kursor.execute(unos_querya,(user_score,ime))
            konekcija.commit()


        session['iskoristena_lista'] = []
        session['score'] = 0
        return redirect(url_for('score'))
  
@app.route('/score')
def score():
    prikazi_query=''' SELECT * 
                    FROM highscore 
                    ORDER BY bodovi DESC 
                    LIMIT 10;
                    '''
    konekcija=sql.connect(baza)
    kursor=konekcija.cursor()
    kursor.execute(prikazi_query)
    highScores=kursor.fetchall()
    top10=[red for red in highScores]
    return render_template('kviz_gameover.html',top10=top10)

if __name__ == '__main__':
    app.run()
