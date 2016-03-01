import os
import re
import datetime
import shutil
import numpy as n
import nltk as k
from percolation.rdf import NS, po, c
import percolation as P


class TranslationPublishing:
    """To be inherited by publishing classes in social,
    gmane and participation packages"""
    def makeTranslation(self):
        """Overwrite in subclasses"""
        pass

    def __init__(self, snapshotid, final_path="some_snapshots/",
                 umbrella_dir=None):
        final_path_ = "{}{}/".format(final_path, snapshotid)
        if not umbrella_dir:
            umbrella_dir = final_path
        online_prefix = \
            "https://raw.githubusercontent.com/OpenLinkedSocialData/\
            {}master/{}/".format(umbrella_dir, snapshotid)
        if not os.path.isdir(final_path):
            os.mkdir(final_path)
        if not os.path.isdir(final_path_):
            os.mkdir(final_path_)
        size_chars_overall = []
        size_tokens_overall = []
        size_sentences_overall = []
        locals_ = locals().copy()
        del locals_["self"]
        for i in locals_:
            exec("self.{}={}".format(i, i))

    def makePostsTriples(self):
        if not self.hastext:
            return
        self.totalchars = sum(self.size_chars_overall)
        self.mchars_messages = n.mean(self.size_chars_overall)
        self.dchars_messages = n.std(self.size_chars_overall)
        self.totaltokens = sum(self.size_tokens_overall)
        self.mtokens_messages = n.mean(self.size_tokens_overall)
        self.dtokens_messages = n.std(self.size_tokens_overall)
        self.totalsentences = sum(self.size_sentences_overall)
        self.msentences_messages = n.mean(self.size_sentences_overall)
        self.dsentences_messages = n.std(self.size_sentences_overall)
        self.nmessages = P.get(
            "SELECT (COUNT(?s) as ?s) WHERE { ?s a po:Message }",
            context=self.translation_graph)
        self.nparticipants = P.get(
            "SELECT (COUNT(?s) as ?s) WHERE { ?s a po:Participant }",
            context=self.translation_graph)
        self.nurls = P.get(
            "SELECT (COUNT(?s) as ?s) WHERE { ?s po:hasUrl ?o }",
            context=self.translation_graph)
        triples = [
             (self.snapshoturi, po.nParticipants,     self.nparticipants),
             (self.snapshoturi, po.nMessages,         self.nmessages),
             (self.snapshoturi, po.nCharsOverall,     self.totalchars),
             (self.snapshoturi, po.mCharsOverall,     self.mchars_messages),
             (self.snapshoturi, po.dCharsOverall,     self.dchars_messages),
             (self.snapshoturi, po.nTokensOverall,    self.totaltokens),
             (self.snapshoturi, po.mTokensOverall,    self.mtokens_messages),
             (self.snapshoturi, po.dTokensOverall,    self.dtokens_messages),
             (self.snapshoturi, po.nSentencesOverall, self.totalsentences),
             (self.snapshoturi, po.mSentencesOverall, self.msentences_messages),
             (self.snapshoturi, po.dSentencesOverall, self.dsentences_messages),
             ]
        P.add(triples, context=self.meta_graph)

    def makeMetadata(self):
        self.makePostsTriples()
        # get participant and message vars from snapshot through queries
        self.participantvars = P.get("""SELECT DISTINCT ?p WHERE { GRAPH <%s> {
                                  ?fooparticipant po:snapshot <%s> .
                                  ?fooparticipant a po:Participant .
                                  ?fooparticipant ?p ?fooobject . } } """ % (
                                self.translation_graph, self.snapshoturi))
        P.rdf.triplesScaffolding(
            self.snapshoturi,
            [po.ParticipantAttribute]*len(self.participantvars),
            self.participantvars, context=self.meta_graph)
        self.messagevars = P.get("""SELECT DISTINCT ?p WHERE { GRAPH <%s> {
                               ?foomessage po:snapshot <%s> .
                               ?foomessage a po:Message .
                               ?foomessage ?p ?fooobject . } } """ % (
                                   self.translation_graph, self.snapshoturi))
        P.rdf.triplesScaffolding(
                self.snapshoturi,
                [po.MessageAttribute]*len(self.messagevars),
                self.messagevars, context=self.meta_graph)

        self.mrdf = self.snapshotid+"Meta.rdf"
        self.mttl = self.snapshotid+"Meta.ttl"
        self.desc = "dataset with snapshotID:\
            {}\nsnapshotURI: {} \nisEgo: {}. isGroup: {}.".format(
            self.snapshotid, self.snapshoturi, self.isego, self.isgroup)
        self.desc += "\nisFriendship: {}; ".format(self.isfriendship)
        self.desc += "isInteraction: {}.".format(self.isinteraction)
        self.desc += "\nhasText: {}".format(self.hastext)
        self.nchecks = P.get(r"SELECT (COUNT(?checker) as ?cs) WHERE { \
                             ?foosession po:checkParticipant ?checker}",
                             context=self.translation_graph)
        self.desc += "\nnParticipants: {}; nInteractions: {} \
            (only session checks in first aa).".format(
                self.nparticipants, self.nchecks)
        self.desc += "\nnMessages: {}; ".format(self.nmessages)
        self.desc += "\nnCharsOverall: {}; mCharsOverall: {};\
            dCharsOverall: {}.".format(self.totalchars, self.mchars_messages,
                                       self.dchars_messages)
        self.desc += "\nnTokensOverall: {}; mTokensOverall: {};\
            dTokensOverall: {};".format(self.totaltokens, self.mtokens_messages,
                                        self.dtokens_messages)
        self.desc += "\nnSentencesOverall: {}; mSentencesOverall: {};\
            dSentencesOverall: {};".format(
                self.totalsentences, self.msentences_messages,
                self.dsentences_messages)
        self.desc += "\nnURLs: {}; nAAMessages {}.".format(
            self.nurls, self.nmessages)
        self.dates = P.get(r"SELECT ?date WHERE { GRAPH <%s> {\
                           ?fooshout po:createdAt ?date } " % (
                               self.translation_graph,))
        self.desc += "\nReference timespan: {} to {}".format(
            min(dates), max(dates))
        self.desc += """\nRDF expression in the XML file(s):
{}
and the Turtle file(s):
{}
(anonymized: {}).""".format(self.translation_xml, self.translation_ttl,
                            self.anonymized)
        self.desc += """\nMetadata of this snapshot in the XML file(s):
{}
and the Turtle file(s):
{}.""".format(self.meta_xml, self.meta_ttl)
        self.desc+="""\nFiles should be available in: \n{}""".format()

        self.desc+="\n\nNote: numeric variables starting with n are countings, with m are means and d are standard deviations."
        if isinstance(self.translation_xml,list):
            P.rdf.triplesScaffolding(self.snapshoturi,
                    [po.translationXMLFilename]*len(self.translation_xml)+[po.translationTTLFilename]*len(self.translation_ttl),
                    self.translation_xml+self.translation_ttl,context=self.meta_graph)
            P.rdf.triplesScaffolding(self.snapshoturi,
                    [po.onlineTranslationXMLFileURI]*len(self.translation_xml)+[po.onlineTranslationTTLFileURI]*len(self.translation_ttl),
                    [self.online_prefix+i for i in self.translation_xml+self.translation_ttl],context=self.meta_graph)
            triples=[
                    (self.snapshoturi,po.translationXMLFilesize,self.translation_size_xml),
                    (self.snapshoturi,po.translationTTLFilesize,self.translation_size_ttl),
                    ]
        else:
            triples=[
                    (self.snapshoturi,po.translationXMLFilename,self.translation_xml),
                    (self.snapshoturi,po.translationXMLFilesize,self.translation_size_xml),
                    (self.snapshoturi,po.translationTTLFilename,self.translation_ttl),
                    (self.snapshoturi,po.translationTTLFilesize,self.translation_size_ttl),
                    ]
        P.add(triples,self.meta_graph)
        triples=[
                (self.snapshoturi, po.triplifiedIn,      datetime.datetime.now()),
                (self.snapshoturi, po.triplifiedBy,      "scripts/"),
#                (self.snapshoturi, po.donatedBy,         self.snapshotid[:-4]),
                (self.snapshoturi, po.availableAt,       self.online_prefix),
                (self.snapshoturi, po.onlineMetaXMLFile, self.online_prefix+self.mrdf),
                (self.snapshoturi, po.onlineMetaTTLFile, self.online_prefix+self.mttl),
                (self.snapshoturi, po.metaXMLFileName,   self.mrdf),
                (self.snapshoturi, po.metaTTLFileName,   self.mttl),
#                (self.snapshoturi, po.acquiredThrough,   "aa shouts in "+self.snapshotid),
                (self.snapshoturi, po.socialProtocolTag, self.social_protocol), # AA, fb, etc
                (self.snapshoturi, po.socialProtocol,    P.rdf.ic(po.Platform,self.social_protocol,self.meta_graph,self.snapshoturi)),
                (self.snapshoturi, po.nTriples,         self.ntranslation_triples),
                (self.snapshoturi, NS.rdfs.comment,         self.desc),
                ]
        P.add(triples,self.meta_graph)

    def writeAll(self):
        g=P.context(self.meta_graph)
        ntriples=len(g)
        triples=[
                 (self.snapshoturi,po.nMetaTriples,ntriples)      ,
                 ]
        P.add(triples,context=self.meta_graph)
        g.namespace_manager.bind("po",po)
        g.serialize(self.final_path_+self.snapshotid+"Meta.ttl","turtle"); c("ttl")
        g.serialize(self.final_path_+self.snapshotid+"Meta.rdf","xml")
        c("serialized meta")
        if not os.path.isdir(self.final_path_+"scripts"):
            os.mkdir(self.final_path_+"scripts")
        shutil.copy(PACKAGEDIR+"/../tests/triplify.py",self.final_path_+"scripts/triplify.py")
        # copia do base data

        self.dates=[i.isoformat() for i in self.dates]
        date1=min(self.dates)
        date2=max(self.dates)
        with open(self.final_path_+"README","w") as f:
            f.write("""::: Open Linked Social Data publication
\nThis repository is a RDF data expression of the IRC
snapshot {snapid} with tweets from {date1} to {date2}
(total of {ntrip} triples).{tinteraction}{tposts}
\nMetadata for discovery in the RDF/XML file:
{mrdf} \nor in the Turtle file:\n{mttl}
\nEgo network: {ise}
Group network: {isg}
Friendship network: {isf}
Interaction network: {isi}
Has text/posts: {ist}
\nAll files should be available at the git repository:
{ava}
\n{desc}

The script that rendered this data publication is on the script/ directory.\n:::""".format(
                snapid=self.snapshotid,date1=date1,date2=date2,ntrip=self.ntriples,
                        tinteraction=tposts,
                        tposts=tposts,
                        mrdf=self.translation_xml,
                        mttl=self.translation_ttl,
                        ise=self.isego,
                        isg=self.isgroup,
                        isf=self.isfriendship,
                        isi=self.isinteraction,
                        ist=self.hastext,
                        ava=self.online_prefix,
                        desc=self.desc
                        ))

    regex_url=re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    def addText(self,messageuri,messagetext):
        size_chars=len(messagetext)
        size_tokens=len(k.wordpunct_tokenize(messagetext))
        size_sentences=len(k.sent_tokenize(  messagetext))
        triples=[
                (messageuri, po.textMessage, messagetext),
                (messageuri, po.nChars,       size_chars),
                (messageuri, po.nTokens,      size_tokens),
                (messageuri, po.nSentences,   size_sentences),
                ]
        urls = self.regex_url.findall(messagetext)
        for url in urls:
            triples+=[
                     (messageuri,po.hasUrl,url),
                     ]
        self.size_chars_overall+=[size_chars]
        self.size_tokens_overall+=[size_tokens]
        self.size_sentences_overall+=[size_sentences]
        return triples
    def writeTranslates(self,mode="full"):
        c("mode full or chunk or multigraph write:",mode)
        if mode=="full":
            g=P.context(self.translation_graph)
            self.translation_ttl=self.snapshotid+"Translation.ttl"
            self.translation_xml=self.snapshotid+"Translation.rdf"
            g.serialize(self.final_path_+self.translation_ttl,"turtle"); c("ttl")
            g.serialize(self.final_path_+self.translation_xml,"xml")
            self.translation_size_ttl=os.path.getsize(self.final_path_+self.translation_ttl)/10**6
            self.translation_size_xml=os.path.getsize(self.final_path_+self.translation_xml)/10**6
            self.ntranslation_triples=len(g)
        elif mode=="chunk":
            # writeByChunks
            raise NotImplementedError("Perform P.utils.writeByChunks on self.translation_graph")
        elif mode=="multigraph":
            raise NotImplementedError("Perform serialize(write) on each of the self.translation_graphs")


