import json
R=json.load(open('/tmp/bachwork/rdfs.json'))
skip_paths={"BWV565/ToccataFugue/","BWV846/wtk1-prelude1/","BWV846/wtk1-prelude1-guitar-duo/","BWV1007/bwv1007/",
"BWV1068/air-tromb/","BWV1068/bach_air_bmv_1068/","BWV1080/rectus/","BWV997/Bach_Preludio_BWV997/","BWV1013/bwv1013_sax/",
"BWV1011/bwv1011_transposed/","BWV609/Lobt/","BWV928/bach-praeludium-10/","BWV997/bwv997-05double/","BWV16/Cantata_16_no_5/",
"BWV582/Passacaglia/","BWV1056/arioso/","BWV269/bwv_269/","BWV347/bwv347/","BWV454/bwv_454/","BWV462/bwv_462/",
"BWV510/BWV-510/","BWV511/BWV-511/","BWV512/BWV-512/","BWV515/anna-magdalena-20a/","BWV516/BWV-516/","BWV693/bwv693/",
"BWV723/bwv723/","BWV724/bwv724/","BWV952/fugue-c-major/","BWV994/bach-applicatio/","BWV117a/BWV-117a/",
"BWVAnh113/anna-magdalena-03/","BWVAnh114/Minuet-xpose/","BWVAnh114/anna-magdalena-04-guitar-tab/","BWVAnh114/anna-magdalena-04-guitar/",
"BWVAnh114/anna-magdalena-114-115-116/","BWVAnh116/anna-magdalena-07/","BWVAnh117b/BWV-117b/","BWVAnh118/BWV-118/","BWVAnh119/BWV-119/",
"BWVAnh120/BWV-120/","BWVAnh121/BWV-121/","BWVAnh127/BWV-127/","BWVAnh128/BWV-128/","BWVAnh691/BWV-691/"}
sel=[r for r in R if 'ShareAlike' not in r['licence'] and r['path'] not in skip_paths]
json.dump(sel,open('/tmp/bachwork/selected.json','w'),indent=1,ensure_ascii=False)
print(len(sel))
