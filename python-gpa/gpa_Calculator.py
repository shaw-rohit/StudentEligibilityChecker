import random
grading_scale = {'usa' :'0-4',
                 'ind':'0-10'}
grading = input('enter the gpa scale')
gpa = float(input('enter the gpa'))

#####converts us gpa to uk gpa
def us_to_uk(score):
    print('comes into the conversion')
    if score == 4:
        return round(random.uniform(70, 99), 2)
    if score < 4 and score >= 3.7:
        return round(random.uniform(65, 69), 2)
    if score < 3.7 and score >= 3.3:
        return round(random.uniform(60, 64), 2)
    if score < 3.3 and score >= 3:
        return round(random.uniform(55, 59), 2)
    if score < 3 and score >= 2.7:
        return round(random.uniform(50, 54), 2)
    if score < 2.7 and score >= 2.3:
        return round(random.uniform(45, 49), 2)
    if score < 2.3 and score >= 2:
        return round(random.uniform(40, 44), 2)
    if score <= 2 and score >= 1:
        return round(random.uniform(35, 39), 2)
    if score < 1:
        return round(random.uniform(0, 35), 2)

#####Converts indian gpa to US gpa
def ind_to_us(score):
    if gpa >= 8.5:
        print(round(random.uniform(3.7, 4.0), 1))
    if gpa >= 8 and gpa <= 8.4:
        print('3.7')
        return 3.7
    if gpa >= 7.5 and gpa <= 7.9:
        return 3.3
    if gpa >= 7 and gpa <= 7.4:
        return 3.0
    if gpa >= 6.5 and gpa <= 6.9:
        return 2.7
    if gpa >= 6.0 and gpa <= 6.4:
        return 2.3
    if gpa >= 5.5 and gpa <= 5.9:
        return 2
    if gpa >= 5.0 and gpa <= 5.4:
        return 1.7
    if gpa < 5:
        return round(random.uniform(0, 1.3), 1)
#####check for grading scale
if  grading in grading_scale['usa']:
    #print('usa conversion')
    ###calls us to uk gpa conversion
    calc_us_gpa = us_to_uk(gpa)
    #print(calc_us_gpa)
else:
    print('carrying india to us conversion first')
    ###converts indian gpa to usa gpa first
    usa_gpa = ind_to_us(gpa)
    #print(usa_gpa)
    ###converts us gpa to uk gpa
    calc_ind_gpa = us_to_uk(usa_gpa)
    #print(calc_ind_gpa)
