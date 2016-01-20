from datetime import datetime
from random import randint, choice
from percolation.rdf import NS, a
from string import ascii_lowercase
import percolation as P
c=P.check

def startSession(context="session"):
    current_user_uri=P.get(NS.per.currentUser) # from rdf.rdflib OK
    now=datetime.now()
    if not current_user_uri:
        nick=randomNick() # OK
        current_user_uri=P.rdf.timestampedURI(NS.per.Participant,nick,now) # rdf.rdflib OK
        triples=[
                (current_user_uri, a, NS.per.DefaultParticipant),
                (current_user_uri, NS.per.nick, nick),
                (current_user_uri, NS.per.registered, now),
                ]
        c("Please create a user with P.utils.createUser() ASAP. Registered for now as {} with URI: {}".format(nick,current_user_uri))
    else:
        triples=[]
    session_uri=P.rdf.timestampedURI(NS.per.Session,nick,now) # from rdf.rdflib OK
    current_status_uri=NS.per.CurrentStatus # class in per: ontology OK
    triples+=[
             (current_status_uri,NS.per.currentSession,session_uri),
             (session_uri,NS.per.started,now),
             (session_uri,NS.per.user,current_user_uri),
             (current_status_uri,NS.per.currentUser,current_user_uri),
             ]
    P.set_(triples,context=context) # from rdf.rdflib OK
    P.rdf.minimumOntology() # from rdf.ontology
    P.legacy.triples.datasets.datasets() # from legacy.triples
    P.rdf.inference.rdfsInference("minimum_ontology","legacy_metadata","session_legacy_metadata") # from rdf.inference
    # by this point, one should have the named graphs/contexts:
    # session, minimum_ontology, legacy_metadata, session_legacy_metadata
def randomNick():
    vowels="aeiouy"
    consonants="".join(i for i in ascii_lowercase if i not in vowels)
    nsyllables=randint(5,10)
    nick="".join(i for j in range(nsyllables) for i in (choice(consonants),choice(vowels)))
    if randint(0,1):
        nick=choice(vowels)+nick
    return nick


