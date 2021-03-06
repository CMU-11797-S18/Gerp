#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  2 23:23:25 2018

@author: eti
"""

def prepro_each(args, data_type, start_ratio=0.0, stop_ratio=1.0, out_name="default", in_path=None):
    if args.tokenizer == "PTB":
        import nltk
        sent_tokenize = nltk.sent_tokenize
        def word_tokenize(tokens):
            return [token.replace("''", '"').replace("``", '"') for token in nltk.word_tokenize(tokens)]
    elif args.tokenizer == 'Stanford':
        from my.corenlp_interface import CoreNLPInterface
        interface = CoreNLPInterface(args.url, args.port)
        sent_tokenize = interface.split_doc
        word_tokenize = interface.split_sent
    else:
        raise Exception()

    if not args.split:
        sent_tokenize = lambda para: [para]
        
        
        
        
    filenames = ['data/searchqa/raw/SearchQA/val.txt', \
                 'data/searchqa/raw/SearchQA/test.txt',\
                 'data/searchqa/raw/SearchQA/train.txt']
    question_id = 1
    for i in range(3):
        fpr = open(filenames[i], 'r')
        q, cq, y, rx, rcx, ids, idxs = [], [], [], [], [], [], []
        cy = []
        x, cx = [], []
        answerss = []
        p = []
        word_counter, char_counter, lower_word_counter = Counter(), Counter(), Counter()
        #fpw = open(filenames_w[i], 'w')
        #fpw_testing = open(filenames_w_testing[i], 'w')
        for line in fpr:
            con = line.strip().split('|||')
            question = con[1].strip()
            answer = con[2].strip()
            #@check -- intialize xp , cxp
            xp, cxp = [], []
            answers = []
            
            
            if len(question) != 0 and len(answer) != 0:
                assert(len(question) > 0)
                assert(len(answer) > 0)
                passages = con[0].strip()[4:-4].split('</s>  <s>')
                assert(len(passages) != 0)
                ##write questions
                qi = word_tokenize(question)
                cqi = [list(qij) for qij in qi]
                ## write answers
                answers.append(answer)
                
                
                #fpw.write(question + '*split_sign*' + str(question_id) + '*split_sign*' + answer + '\n')
                pp = []
                #@ check pp , rank paragraphs and take only1 (similar to squad)
                for context in passages:
                    assert(len(context)>0)
                    #pp.append(context)
                    
                    xi = list(map(word_tokenize, sent_tokenize(context)))
                    xi = [process_tokens(tokens) for tokens in xi]  # process tokens
                    # given xi, add chars
                    cxi = [[list(xijk) for xijk in xij] for xij in xi]
                    xp.append(xi)
                    cxp.append(cxi)
                    pp.append(context)
                    
                    #@check
                    for xij in xi:
                        for xijk in xij:
                            word_counter[xijk] +=1
                            lower_word_counter[xijk.lower()] += 1 #len(para['qas'])
                            for xijkl in xijk:
                                char_counter[xijkl] +=  1 #len(para['qas'])

                    #fpw.write(p + '*split_sign*' + '0\n')
                #fpw.write('*new_instance*\n')
                #fpw_testing.write( str(question_id) + '\t' + answer + '\n' )
                
                for qij in qi:
                    word_counter[qij] += 1
                    lower_word_counter[qij.lower()] += 1
                    for qijk in qij:
                        char_counter[qijk] += 1
                        
                        
                
        
                        
                        
                question_id += 1
                q.append(qi)
                cq.append(cqi)
                #y.append(yi)
                #cy.append(cyi)
                #rx.append(rxi)
                #rcx.append(rxi)
                ids.append(question_id)
                idxs.append(len(idxs))
                answerss.append(answers)
                p.append(pp)
                
            if args.debug:
                break

        word2vec_dict = get_word2vec(args, word_counter)
        lower_word2vec_dict = get_word2vec(args, lower_word_counter)

        # add context here
        data = {'q': q, 'cq': cq, 'y': y, '*x': rx, '*cx': rcx, 'cy': cy,
            'idxs': idxs, 'ids': ids, 'answerss': answerss, '*p': rx}
        shared = {'x': x, 'cx': cx, 'p': p,
              'word_counter': word_counter, 'char_counter': char_counter, 'lower_word_counter': lower_word_counter,
              'word2vec': word2vec_dict, 'lower_word2vec': lower_word2vec_dict}

        print("saving ...")
        save(args, data, shared, out_name)
                

        #print(question_id)
        #fpw_testing.close()
        #fpr.close()
        #fpw.close()
   
        

    #source_path = in_path or os.path.join(args.source_dir, "{}-v1.1.json".format(data_type))
    #source_data = json.load(open(source_path, 'r'))

   
    #start_ai = int(round(len(source_data['data']) * start_ratio))
    #stop_ai = int(round(len(source_data['data']) * stop_ratio))
    """
    for ai, article in enumerate(tqdm(source_data['data'][start_ai:stop_ai])):
        # ai --> represents topic out of 48 topics (for example id for suber bowl)
        xp, cxp = [], []
        pp = []
        x.append(xp)
        cx.append(cxp)
        p.append(pp)
        #article -- title , paragraphs
        for pi, para in enumerate(article['paragraphs']):
            #pi - paragraph number for ai
            # wordss
            context = para['context']
            context = context.replace("''", '" ')
            context = context.replace("``", '" ')
            xi = list(map(word_tokenize, sent_tokenize(context)))
            xi = [process_tokens(tokens) for tokens in xi]  # process tokens
            # given xi, add chars
            cxi = [[list(xijk) for xijk in xij] for xij in xi]
            xp.append(xi)
            cxp.append(cxi)
            pp.append(context)

            for xij in xi:
                for xijk in xij:
                    word_counter[xijk] += len(para['qas'])
                    lower_word_counter[xijk.lower()] += len(para['qas'])
                    for xijkl in xijk:
                        char_counter[xijkl] += len(para['qas'])

            rxi = [ai, pi]
            assert len(x) - 1 == ai
            assert len(x[ai]) - 1 == pi
            for qa in para['qas']:
                # get words
                qi = word_tokenize(qa['question'])
                cqi = [list(qij) for qij in qi]
                yi = []
                cyi = []
                answers = []
                for answer in qa['answers']:
                    answer_text = answer['text']
                    answers.append(answer_text)
                    answer_start = answer['answer_start']
                    answer_stop = answer_start + len(answer_text)
                    # TODO : put some function that gives word_start, word_stop here
                    yi0, yi1 = get_word_span(context, xi, answer_start, answer_stop)
                    # yi0 = answer['answer_word_start'] or [0, 0]
                    # yi1 = answer['answer_word_stop'] or [0, 1]
                    assert len(xi[yi0[0]]) > yi0[1]
                    assert len(xi[yi1[0]]) >= yi1[1]
                    w0 = xi[yi0[0]][yi0[1]]
                    w1 = xi[yi1[0]][yi1[1]-1]
                    i0 = get_word_idx(context, xi, yi0)
                    i1 = get_word_idx(context, xi, (yi1[0], yi1[1]-1))
                    cyi0 = answer_start - i0
                    cyi1 = answer_stop - i1 - 1
                    # print(answer_text, w0[cyi0:], w1[:cyi1+1])
                    assert answer_text[0] == w0[cyi0], (answer_text, w0, cyi0)
                    assert answer_text[-1] == w1[cyi1]
                    assert cyi0 < 32, (answer_text, w0)
                    assert cyi1 < 32, (answer_text, w1)

                    yi.append([yi0, yi1])
                    cyi.append([cyi0, cyi1])

                for qij in qi:
                    word_counter[qij] += 1
                    lower_word_counter[qij.lower()] += 1
                    for qijk in qij:
                        char_counter[qijk] += 1
                """
                