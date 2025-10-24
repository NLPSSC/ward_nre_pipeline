import io
import csv
import sys
import json
from pathlib import Path
from typing import List, Tuple
from loguru import logger

logger.remove()
logger.add(
    sink=sys.stderr,
    enqueue=True,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

example_csv_data = """
note_id|ngram|term|cui|similarity|semtypes|pos_start|pos_end
PMC6094735|predisposition|Predisposition|C0012655|0.8461538461538461|{'T201'}|2475|2489
PMC6094735|eldest child|Oldest child|C0337546|0.8181818181818182|{'T033'}|1004|1016
PMC6094735|dental arch|Dental arch|C0011325|0.8|{'T023'}|2195|2206
PMC6094735|dental arch|Dental arch|C1280374|0.8|{'T023'}|2195|2206
PMC6094735|examination|Examination|C0031809|0.8|{'T058'}|3057|3068
PMC6094736|Teeth|Teeth|C0040426|1.0|{'T023'}|2456|2461
PMC6094736|supernumerary teeth|Supernumerary teeth|C5441989|0.8888888888888888|{'T047'}|1377|1396
PMC6094736|supernumerary teeth|Supernumerary teeth|C5441989|0.8888888888888888|{'T047'}|1692|1711
PMC6094736|permanent teeth|Permanent teeth|C0348070|0.8571428571428571|{'T023'}|1573|1588
PMC6094737|existing condition|Pre-existing condition|C0521987|0.8|{'T033'}|1961|1979
PMC6094739|and tooth|Band tooth|C0399130|0.875|{'T061'}|339|353
PMC6094739|had circulation|Bad circulation|C0425711|0.8571428571428571|{'T033'}|1188|1206
PMC6094739|crown of tooth|Crown of tooth|C0226993|0.8461538461538461|{'T023'}|412|430
PMC6094739|organization|Organization|C0029237|0.8181818181818182|{'T039'}|1076|1088
PMC6094739|organization|Organization|C0029237|0.8181818181818182|{'T039'}|1363|1375
PMC6094739|organization|Organization|C0029237|0.8181818181818182|{'T039'}|1656|1668
PMC6094740|instructions|Construction|C0441513|0.8181818181818182|{'T061'}|2955|2967
PMC6094740|restoration|Restoration|C0449982|0.8|{'T170'}|1562|1573
PMC6094740|association|Association|C0004083|0.8|{'T041'}|5085|5096
PMC6094741|Surgical|Surgical|C0543467|1.0|{'T061'}|29|37
PMC6094741|Ligament|Ligament|C1269080|1.0|{'T023'}|271|279
PMC6094741|Surgical|Surgical|C0543467|1.0|{'T061'}|902|910
PMC6094741|Jaw|Jaw|C0022359|1.0|{'T023'}|1872|1875
PMC6094741|Jaw|Jaw|C1273020|1.0|{'T029'}|1872|1875
PMC6094741|And|And|C1706368|1.0|{'T170'}|4816|4819
PMC6094741|And|And|C1706368|1.0|{'T170'}|6262|6265
PMC6094741|And|And|C1706368|1.0|{'T170'}|6733|6736
PMC6094741|And|And|C1706368|1.0|{'T170'}|7638|7641
PMC6094741|And|And|C1706368|1.0|{'T170'}|10366|10369
PMC6094741|And|And|C1706368|1.0|{'T170'}|11244|11247
PMC6094741|And|And|C1706368|1.0|{'T170'}|12757|12760
PMC6094741|one operation|Bone operation|C0185131|0.9166666666666666|{'T061'}|9750|9763
PMC6094741|and tooth|Band tooth|C0399130|0.875|{'T061'}|9244|9257
PMC6094741|and tooth|Band tooth|C0399130|0.875|{'T061'}|9717|9730
PMC6094741|crown of tooth|Crown of tooth|C0226993|0.8461538461538461|{'T023'}|6550|6568
PMC6094741|crown of tooth|Crown of tooth|C0226993|0.8461538461538461|{'T023'}|13235|13253
PMC6094741|neck of tooth|Neck of tooth|C0447366|0.8333333333333334|{'T023'}|6672|6689
PMC6094741|intervention|Intervention|C1273869|0.8181818181818182|{'T058'}|7247|7259
PMC6094741|inflammation|Inflammation|C0021368|0.8181818181818182|{'T046'}|8862|8874
PMC6094741|obstruction|Obstruction|C0028778|0.8|{'T033'}|2198|2209
PMC6094741|examination|Examination|C0031809|0.8|{'T058'}|8460|8471
PMC6094741|obstruction|Obstruction|C0028778|0.8|{'T033'}|9231|9242
PMC6094741|observation|Observation|C0557985|0.8|{'T061'}|13111|13122
PMC6094741|attachment|Reattachment|C0185042|0.8|{'T061'}|2142|2152
PMC6094741|attachment|Reattachment|C0185042|0.8|{'T061'}|7411|7421
PMC6094741|difference|Indifference|C0085632|0.8|{'T048'}|8562|8572
PMC6094741|attachment|Reattachment|C0185042|0.8|{'T061'}|12459|12469
PMC6094741|flammation|Inflammation|C0021368|0.8|{'T046'}|13143|13153
PMC6094741|lation|Elation|C0233492|0.8|{'T033'}|5880|5886
PMC6094742|Surgery|Surgery|C0543467|1.0|{'T061'}|93|100
PMC6094742|English|English|C3540738|1.0|{'T170'}|876|883
PMC6094742|English|English|C3540738|1.0|{'T170'}|1307|1314
PMC6094742|and finding|Hand finding|C0575800|0.9|{'T033'}|8182|8193
PMC6094742|ptyalism|Aptyalism|C0043352|0.8571428571428571|{'T047'}|6011|6019
PMC6094742|discrimination|Discrimination|C0012632|0.8461538461538461|{'T041'}|2955|2969
PMC6094742|application|Application|C0185125|0.8|{'T061'}|6868|6879
PMC6094742|tartar|Tartar|C0011330|0.75|{'T033'}|7528|7534
PMC6094742|independence|Dependence|C0439857|0.7|{'T048'}|1659|1671
PMC6094743|Extraction|Extraction|C0185115|1.0|{'T061'}|1670|1680
PMC6094743|Dentition|Dentition|C0011443|1.0|{'T023'}|390|399
PMC6094743|Dentition|Dentition|C0011443|1.0|{'T023'}|481|490
PMC6094743|Dentition|Dentition|C0011443|1.0|{'T023'}|1197|1206
PMC6094743|Dentition|Dentition|C0011443|1.0|{'T023'}|1517|1526
PMC6094743|Dentition|Dentition|C0011443|1.0|{'T023'}|2216|2225
PMC6094743|Diseases|Diseases|C0012634|1.0|{'T047'}|907|915
PMC6094743|History|History|C0262926|1.0|{'T033'}|140|147
PMC6094743|History|History|C5399914|1.0|{'T170'}|140|147
PMC6094743|Surgery|Surgery|C0543467|1.0|{'T061'}|437|444
PMC6094743|History|History|C0262926|1.0|{'T033'}|758|765
PMC6094743|History|History|C5399914|1.0|{'T170'}|758|765
PMC6094743|Advice|Advice|C0150600|1.0|{'T058'}|3852|3858
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|157|162
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|272|277
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|544|549
PMC6094743|Guide|Guide|C0302614|1.0|{'T074'}|713|718
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|769|774
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|810|815
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|919|924
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|978|983
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|1905|1910
PMC6094743|Mouth|Mouth|C0230028|1.0|{'T029'}|2596|2601
PMC6094743|Mouth|Mouth|C1267547|1.0|{'T029'}|2596|2601
PMC6094743|Mouth|Mouth|C1278910|1.0|{'T029'}|2596|2601
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|2606|2611
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|3014|3019
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|3207|3212
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|3435|3440
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|3927|3932
PMC6094743|Guide|Guide|C0302614|1.0|{'T074'}|3980|3985
PMC6094743|Teeth|Teeth|C0040426|1.0|{'T023'}|3995|4000
PMC6094743|Jules|Jules|C0445513|1.0|{'T170'}|4144|4149
PMC6094743|Fons|Fons|C0444939|1.0|{'T170'}|692|696
PMC6094743|Directions|Direction|C0522247|0.875|{'T041'}|594|604
PMC6094743|Instructions|Construction|C0441513|0.8181818181818182|{'T061'}|3789|3801
PMC6094743|Palates|Palate|C0700374|0.8|{'T023'}|866|873
PMC6094743|Palates|Palate|C1278914|0.8|{'T023'}|866|873
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|34|43
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|371|380
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|4535|4544
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|4747|4756
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|6305|6314
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|6775|6784
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|9162|9171
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|10259|10268
PMC6094744|Dentition|Dentition|C0011443|1.0|{'T023'}|11717|11726
PMC6094744|extraction of tooth|Extraction of tooth|C0040440|0.8888888888888888|{'T061'}|9275|9296
PMC6094744|examine|Hexamine|C0025638|0.8333333333333334|{'T109', 'T121'}|3363|3370
PMC6094744|mission|Emission|C0233929|0.8333333333333334|{'T031'}|7123|7130
PMC6094744|introduction|Introduction|C1293116|0.8181818181818182|{'T061'}|3913|3925
PMC6094744|indifference|Indifference|C0085632|0.8181818181818182|{'T048'}|9671|9683
PMC6094744|mastication|Mastication|C0024888|0.8|{'T040'}|2480|2491
PMC6094744|dental arch|Dental arch|C0011325|0.8|{'T023'}|3012|3023
PMC6094744|dental arch|Dental arch|C1280374|0.8|{'T023'}|3012|3023
PMC6094744|observation|Observation|C0557985|0.8|{'T061'}|4915|4926
PMC6094744|observation|Observation|C0557985|0.8|{'T061'}|9090|9101
PMC6094744|destruction|Destruction|C1261381|0.8|{'T061'}|10485|10496
PMC6094744|cases of disease|Types of diseases|C0457464|0.75|{'T170'}|3483|3499
PMC6094744|tartar|Tartar|C0011330|0.75|{'T033'}|4101|4107
PMC6094752|And|And|C1706368|1.0|{'T170'}|7226|7229
PMC6094752|personal appearance|Personal appearance|C0424459|0.8888888888888888|{'T033'}|6024|6043
PMC6094752|personal appearance|Personal appearance|C0424459|0.8888888888888888|{'T033'}|7257|7276
PMC6094752|digestive organs|Digestive organ|C0227435|0.8|{'T023'}|8130|8146
PMC6094752|digestive organs|Digestive organ|C1280837|0.8|{'T023'}|8130|8146
PMC6094752|destruction|Destruction|C1261381|0.8|{'T061'}|2110|2121
PMC6094752|restoration|Restoration|C0449982|0.8|{'T170'}|8919|8930
PMC6094752|discoloured|Discoloured|C0332572|0.8|{'T033'}|10288|10299
PMC6094752|tartar|Tartar|C0011330|0.75|{'T033'}|2558|2564
PMC6094752|tartar|Tartar|C0011330|0.75|{'T033'}|6356|6362
PMC6094752|tartar|Tartar|C0011330|0.75|{'T033'}|6581|6587
PMC6094755|Medicine|Medicine|C0013227|1.0|{'T121'}|2619|2627
PMC6094755|Surgery|Surgery|C0543467|1.0|{'T061'}|2632|2639
PMC6094755|Happy|Happy|C0018592|1.0|{'T041'}|25211|25216
PMC6094755|Will|Will|C0042950|1.0|{'T041'}|14946|14950
PMC6094755|Once|Once|C1720092|1.0|{'T170'}|19613|19617
PMC6094755|And|And|C1706368|1.0|{'T170'}|6763|6766
PMC6094755|And|And|C1706368|1.0|{'T170'}|7298|7301
PMC6094755|And|And|C1706368|1.0|{'T170'}|9490|9493
PMC6094755|And|And|C1706368|1.0|{'T170'}|25293|25296
PMC6094755|personal appearance|Personal appearance|C0424459|0.8888888888888888|{'T033'}|14793|14812
PMC6094755|conscientious|Conscientious|C0580939|0.8333333333333334|{'T033'}|15036|15049
PMC6094755|compensation|Decompensation|C0231187|0.8333333333333334|{'T033'}|16958|16970
PMC6094755|compensation|Compensation|C0152057|0.8181818181818182|{'T041'}|16958|16970
PMC6094755|compensation|Compensation|C0152058|0.8181818181818182|{'T039'}|16958|16970
PMC6094755|incompetence|Incompetence|C0231189|0.8181818181818182|{'T046'}|22417|22429
PMC6094755|delinquency|Delinquency|C0522174|0.8|{'T048'}|2324|2335
PMC6094755|destruction|Destruction|C1261381|0.8|{'T061'}|6632|6643
PMC6094755|intercourse|Intercourse|C0009253|0.8|{'T040'}|10032|10043
PMC6094755|intercourse|Intercourse|C0009253|0.8|{'T040'}|10734|10745
PMC6094755|intercourse|Intercourse|C0009253|0.8|{'T040'}|19357|19368
PMC6094755|certificate|Certificate|C0586303|0.8|{'T170'}|21797|21808
PMC6094755|competence|Incompetence|C0231189|0.8|{'T046'}|21822|21832
PMC6094755|mental|Omental|C0028977|0.8|{'T023'}|11334|11340
PMC6094755|mental|Omental|C0028977|0.8|{'T023'}|21983|21989
PMC6094755|mental|Omental|C0028977|0.8|{'T023'}|22188|22194
PMC6094756|Association|Association|C0004083|1.0|{'T041'}|67|78
PMC6094756|and standing|Found standing|C1998219|0.75|{'T033'}|260|272
PMC6094757|Diseases|Diseases|C0012634|1.0|{'T047'}|90|98
PMC6094757|Temple|Temple|C0935456|1.0|{'T029'}|944|950
PMC6094757|Enamel|Enamel|C0011350|1.0|{'T031'}|3726|3732
PMC6094757|Teeth|Teeth|C0040426|1.0|{'T023'}|106|111
PMC6094757|Teeth|Teeth|C0040426|1.0|{'T023'}|6737|6742
PMC6094757|Teeth|Teeth|C0040426|1.0|{'T023'}|6753|6758
PMC6094757|Observations|Observation|C0557985|0.9|{'T061'}|35|47
PMC6094757|permanent teeth|Permanent teeth|C0348070|0.8571428571428571|{'T023'}|4574|4589
PMC6094757|grinding teeth|Grinding teeth|C0006325|0.8461538461538461|{'T048'}|2693|2707
PMC6094757|grinding teeth|Grinding teeth|C0006325|0.8461538461538461|{'T048'}|4974|4988
PMC6094757|Diseased|Disease|C0012634|0.8333333333333334|{'T047'}|6728|6736
PMC6094757|Diseased|Disease|C0012634|0.8333333333333334|{'T047'}|6744|6752
PMC6094759|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|1081|1094
PMC6094759|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|1081|1094
PMC6094759|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|10334|10347
PMC6094759|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|10334|10347
PMC6094759|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|11145|11158
PMC6094759|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|11145|11158
PMC6094759|grinding teeth|Grinding teeth|C0006325|0.8461538461538461|{'T048'}|6964|6978
PMC6094759|investigations|Investigations|C1261322|0.8461538461538461|{'T058'}|8760|8774
PMC6094759|investigations|Investigations|C1261322|0.8461538461538461|{'T058'}|9727|9741
PMC6094759|compensation|Decompensation|C0231187|0.8333333333333334|{'T033'}|11644|11656
PMC6094759|compensation|Compensation|C0152057|0.8181818181818182|{'T041'}|11644|11656
PMC6094759|compensation|Compensation|C0152058|0.8181818181818182|{'T039'}|11644|11656
PMC6094759|inflammation|Inflammation|C0021368|0.8181818181818182|{'T046'}|3984|3996
PMC6094759|examination|Examination|C0031809|0.8|{'T058'}|411|422
PMC6094759|or symptom|Odor symptom|C1271070|0.8|{'T033'}|4057|4067
PMC6094759|generation|Degeneration|C0011164|0.8|{'T046'}|4206|4216
PMC6094759|generation|Regeneration|C0349676|0.8|{'T058'}|4206|4216
PMC6094759|difference|Indifference|C0085632|0.8|{'T048'}|8053|8063
PMC6094759|amputation|Reamputation|C0184917|0.8|{'T061'}|8843|8853
PMC6094759|Period|Periods|C0025344|0.8|{'T040'}|59|65
PMC6094759|Period|Periods|C0025344|0.8|{'T040'}|4095|4101
PMC6094761|Medicine|Medicine|C0013227|1.0|{'T121'}|143|151
PMC6094761|Diseases|Diseases|C0012634|1.0|{'T047'}|353|361
PMC6094761|Teeth|Teeth|C0040426|1.0|{'T023'}|369|374
PMC6094761|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|3509|3522
PMC6094761|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|3509|3522
PMC6094761|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|12762|12775
PMC6094761|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|12762|12775
PMC6094761|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|13573|13586
PMC6094761|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|13573|13586
PMC6094761|Observations|Observation|C0557985|0.9|{'T061'}|297|309
PMC6094761|grinding teeth|Grinding teeth|C0006325|0.8461538461538461|{'T048'}|9392|9406
PMC6094761|investigations|Investigations|C1261322|0.8461538461538461|{'T058'}|11188|11202
PMC6094761|investigations|Investigations|C1261322|0.8461538461538461|{'T058'}|12155|12169
PMC6094761|general observations|General observation|C0588388|0.8421052631578947|{'T058'}|223|243
PMC6094761|compensation|Decompensation|C0231187|0.8333333333333334|{'T033'}|14072|14084
PMC6094761|compensation|Compensation|C0152057|0.8181818181818182|{'T041'}|14072|14084
PMC6094761|compensation|Compensation|C0152058|0.8181818181818182|{'T039'}|14072|14084
PMC6094761|inflammation|Inflammation|C0021368|0.8181818181818182|{'T046'}|6412|6424
PMC6094761|examination|Examination|C0031809|0.8|{'T058'}|2839|2850
PMC6094761|or symptom|Odor symptom|C1271070|0.8|{'T033'}|6485|6495
PMC6094761|generation|Degeneration|C0011164|0.8|{'T046'}|6634|6644
PMC6094761|generation|Regeneration|C0349676|0.8|{'T058'}|6634|6644
PMC6094761|difference|Indifference|C0085632|0.8|{'T048'}|10481|10491
PMC6094761|amputation|Reamputation|C0184917|0.8|{'T061'}|11271|11281
PMC6094761|Period|Periods|C0025344|0.8|{'T040'}|2487|2493
PMC6094761|Period|Periods|C0025344|0.8|{'T040'}|6523|6529
PMC6094762|Then|Then|C1720594|1.0|{'T170'}|1303|1307
PMC6094762|extract tooth|Extract tooth|C0040440|0.8333333333333334|{'T061'}|3176|3193
PMC6094762|lengthening|Lengthening|C0441592|0.8|{'T061'}|2558|2569
PMC6094763|Extraction|Extraction|C0185115|1.0|{'T061'}|6031|6041
PMC6094763|Neglect|Neglect|C0521874|1.0|{'T033'}|5826|5833
PMC6094763|Disease|Disease|C0012634|1.0|{'T047'}|9184|9191
PMC6094763|Pain|Pain|C0030193|1.0|{'T184'}|6243|6247
PMC6094763|Pale|Pale|C0678215|1.0|{'T033'}|6338|6342
PMC6094763|And|And|C1706368|1.0|{'T170'}|2291|2294
PMC6094763|And|And|C1706368|1.0|{'T170'}|3632|3635
PMC6094763|And|And|C1706368|1.0|{'T170'}|6380|6383
PMC6094763|Now|Now|C1720566|1.0|{'T170'}|6427|6430
PMC6094763|And|And|C1706368|1.0|{'T170'}|7009|7012
PMC6094763|And|And|C1706368|1.0|{'T170'}|7888|7891
PMC6094763|And|And|C1706368|1.0|{'T170'}|8246|8249
PMC6094763|And|And|C1706368|1.0|{'T170'}|8424|8427
PMC6094763|And|And|C1706368|1.0|{'T170'}|8832|8835
PMC6094763|And|And|C1706368|1.0|{'T170'}|9362|9365
PMC6094763|and tooth|Band tooth|C0399130|0.875|{'T061'}|7351|7360
PMC6094763|and pain|Hand pain|C0239833|0.8571428571428571|{'T184'}|9192|9200
PMC6094763|imagination|Imagination|C0020913|0.8|{'T041'}|1410|1421
PMC6094763|inattention|Inattention|C0424101|0.8|{'T048'}|5597|5608
PMC6094764|Observations|Observation|C0557985|0.9|{'T061'}|180|192
PMC6094764|.Diseases|Diseases|C0012634|0.8571428571428571|{'T047'}|236|245
PMC6094764|general observations|General observation|C0588388|0.8421052631578947|{'T058'}|117|137
PMC6094764|thoracic duct|Thoracic duct|C0039979|0.8333333333333334|{'T023'}|5842|5855
PMC6094764|much better|Much better|C3841449|0.8|{'T033'}|3180|3191
PMC6094764|attachment|Reattachment|C0185042|0.8|{'T061'}|3506|3516
PMC6094764|Period|Periods|C0025344|0.8|{'T040'}|284|290
PMC6094764|Period|Periods|C0025344|0.8|{'T040'}|1710|1716
PMC6094764|Period|Periods|C0025344|0.8|{'T040'}|4843|4849
PMC6094765|Medicine|Medicine|C0013227|1.0|{'T121'}|26838|26846
PMC6094765|Medicine|Medicine|C0013227|1.0|{'T121'}|30641|30649
PMC6094765|Flashes|Flashes|C0085635|1.0|{'T047'}|17764|17771
PMC6094765|Surgery|Surgery|C0543467|1.0|{'T061'}|19843|19850
PMC6094765|Surgery|Surgery|C0543467|1.0|{'T061'}|20260|20267
PMC6094765|Then|Then|C1720594|1.0|{'T170'}|6186|6190
PMC6094765|Some|Some|C3540770|1.0|{'T170'}|11845|11849
PMC6094765|Then|Then|C1720594|1.0|{'T170'}|27651|27655
PMC6094765|And|And|C1706368|1.0|{'T170'}|2034|2037
PMC6094765|And|And|C1706368|1.0|{'T170'}|5961|5964
PMC6094765|And|And|C1706368|1.0|{'T170'}|13034|13037
PMC6094765|And|And|C1706368|1.0|{'T170'}|17673|17676
PMC6094765|application of bandage|Application of bandage|C0150468|0.9047619047619048|{'T061'}|20431|20455
PMC6094765|reduction of fracture|Reduction of fracture|C1112432|0.9|{'T061'}|20333|20356
PMC6094765|symptomatic|Asymptomatic|C0231221|0.9|{'T033'}|15537|15548
PMC6094765|symptomatic|Asymptomatic|C0332151|0.9|{'T033'}|15537|15548
PMC6094765|morbid conditions|Comorbid conditions|C1275743|0.8823529411764706|{'T033'}|16001|16018
PMC6094765|morbid conditions|Comorbid conditions|C1275743|0.8823529411764706|{'T033'}|18293|18310
PMC6094765|amputation of arm|Amputation of arm|C0186399|0.875|{'T061'}|20298|20318
PMC6094765|source of disease|Source of disease|C0449422|0.875|{'T033'}|16464|16481
PMC6094765|fully conscious|Fully conscious|C0424523|0.8571428571428571|{'T033'}|27179|27194
PMC6094765|morbid condition|Comorbid conditions|C1275743|0.8235294117647058|{'T033'}|17180|17196
PMC6094765|organization|Organization|C0029237|0.8181818181818182|{'T039'}|20575|20587
PMC6094765|organization|Organization|C0029237|0.8181818181818182|{'T039'}|21345|21357
PMC6094765|much better|Much better|C3841449|0.8|{'T033'}|9281|9292
PMC6094765|observation|Observation|C0557985|0.8|{'T061'}|11380|11391
PMC6094765|dental arch|Dental arch|C0011325|0.8|{'T023'}|17658|17669
PMC6094765|dental arch|Dental arch|C1280374|0.8|{'T023'}|17658|17669
PMC6094765|dislocation|Dislocation|C0012691|0.8|{'T037'}|20360|20371
PMC6094765|observation|Observation|C0557985|0.8|{'T061'}|27302|27313
PMC6094765|deficiency|K deficiency|C0032827|0.8|{'T047'}|26340|26350
PMC6094765|employment|Unemployment|C0041674|0.8|{'T033'}|27581|27591
PMC6094766|Disease|Disease|C0012634|1.0|{'T047'}|26|33
PMC6094766|Nothing|Nothing|C0442735|1.0|{'T033'}|4316|4323
PMC6094766|Disease|Disease|C0012634|1.0|{'T047'}|6228|6235
PMC6094766|Teeth|Teeth|C0040426|1.0|{'T023'}|75|80
PMC6094766|Fever|Fever|C0015967|1.0|{'T184'}|10253|10258
PMC6094766|Delta|Delta|C0439097|1.0|{'T170'}|10350|10355
PMC6094766|Tooth|Tooth|C0040426|1.0|{'T023'}|20179|20184
PMC6094766|Tooth|Tooth|C1281562|1.0|{'T023'}|20179|20184
PMC6094766|Now|Now|C1720566|1.0|{'T170'}|8407|8410
PMC6094766|And|And|C1706368|1.0|{'T170'}|12692|12695
PMC6094766|and structure|Hand structure|C3714557|0.9166666666666666|{'T023'}|2943|2956
PMC6094766|and structure|Gland structure|C1285092|0.8461538461538461|{'T023'}|2943|2956
PMC6094766|excessive salivation|Excessive salivation|C0037036|0.8947368421052632|{'T047'}|11384|11404
PMC6094766|functional disorder|Functional disorder|C0277785|0.8888888888888888|{'T046'}|11576|11595
PMC6094766|salivary calculus|Salivary calculus|C0036091|0.875|{'T047'}|15488|15505
PMC6094766|salivary calculus|Salivary calculus|C4316915|0.875|{'T031'}|15488|15505
PMC6094766|sulphuric acid|Sulphuric acid|C0038784|0.8461538461538461|{'T121', 'T197'}|16205|16219
PMC6094766|intermittent fevers|Intermittent fever|C0277799|0.8333333333333334|{'T033'}|7213|7232
PMC6094766|conscientious|Conscientious|C0580939|0.8333333333333334|{'T033'}|18147|18160
PMC6094766|organization|Organization|C0029237|0.8181818181818182|{'T039'}|11823|11835
PMC6094766|destruction|Destruction|C1261381|0.8|{'T061'}|8906|8917
PMC6094766|destruction|Destruction|C1261381|0.8|{'T061'}|11245|11256
PMC6094766|molar tooth|Molar tooth|C0026367|0.8|{'T023'}|15664|15675
PMC6094766|application|Application|C0185125|0.8|{'T061'}|19824|19835
PMC6094766|application|Application|C0185125|0.8|{'T061'}|20257|20268
PMC6094766|generation|Degeneration|C0011164|0.8|{'T046'}|6798|6808
PMC6094766|generation|Regeneration|C0349676|0.8|{'T058'}|6798|6808
PMC6094766|generation|Degeneration|C0011164|0.8|{'T046'}|6812|6822
PMC6094766|generation|Regeneration|C0349676|0.8|{'T058'}|6812|6822
PMC6094766|difference|Indifference|C0085632|0.8|{'T048'}|10514|10524
PMC6094766|ganization|Organization|C0029237|0.8|{'T039'}|10629|10639
PMC6094766|generation|Degeneration|C0011164|0.8|{'T046'}|11649|11659
PMC6094766|generation|Regeneration|C0349676|0.8|{'T058'}|11649|11659
PMC6094766|generation|Degeneration|C0011164|0.8|{'T046'}|11663|11673
PMC6094766|generation|Regeneration|C0349676|0.8|{'T058'}|11663|11673
PMC6094766|difference|Indifference|C0085632|0.8|{'T048'}|14531|14541
PMC6094766|plantation|Replantation|C0035139|0.8|{'T061'}|14712|14722
PMC6094766|plantation|Replantation|C0185042|0.8|{'T061'}|14712|14722
PMC6094766|plantation|Implantation|C0021107|0.8|{'T061'}|14712|14722
PMC6094766|independent|Independent|C1299583|0.7777777777777778|{'T033'}|3065|3076
PMC6094767|ALVEOLAR ABSCESS|Alveolar abscess|C1328248|0.8666666666666667|{'T047'}|39|55
PMC6094767|lower teeth|Lower teeth|C0447211|0.8|{'T029'}|600|611
PMC6094785|Amalgam|Amalgam|C0580619|1.0|{'T130'}|6709|6716
PMC6094785|Silver|Silver|C0037125|1.0|{'T121', 'T196'}|6720|6726
PMC6094785|Silver|Silver|C1318876|1.0|{'T130'}|6720|6726
PMC6094785|close observation|Close observation|C0581528|0.875|{'T061'}|822|839
PMC6094785|close observation|Nose observation|C1269534|0.8125|{'T033'}|822|839
PMC6094785|wearing|Swearing|C0233730|0.8333333333333334|{'T033'}|4854|4861
PMC6094785|wearing|Swearing|C0233730|0.8333333333333334|{'T033'}|5287|5294
PMC6094785|inflammation|Inflammation|C0021368|0.8181818181818182|{'T046'}|3083|3095
PMC6094785|certificates|Certificates|C0586303|0.8181818181818182|{'T170'}|4051|4063
PMC6094785|observation|Observation|C0557985|0.8|{'T061'}|2349|2360
PMC6094785|discontinue|Discontinue|C1706472|0.8|{'T170'}|6817|6828
PMC6094787|Respiration|Respiration|C0035203|1.0|{'T039'}|3794|3805
PMC6094787|Exostosis|Exostosis|C1442903|1.0|{'T047'}|76|85
PMC6094787|And|And|C1706368|1.0|{'T170'}|1223|1226
PMC6094787|purulent discharge|Purulent discharge|C0333274|0.8823529411764706|{'T184'}|909|927
PMC6094787|purulent discharge|Purulent discharge|C1305623|0.8823529411764706|{'T031'}|909|927
PMC6094787|purulent discharge|Mucopurulent discharge|C0302307|0.8|{'T031'}|909|927
PMC6094787|purulent discharge|Mucopurulent discharge|C5240004|0.8|{'T184'}|909|927
PMC6094787|acute inflammation|Acute inflammation|C0333361|0.8823529411764706|{'T033'}|3925|3943
PMC6094787|acute inflammation|Subacute inflammation|C0333383|0.8421052631578947|{'T046'}|3925|3943
PMC6094787|alveolar process|Alveolar process|C0002386|0.8666666666666667|{'T023'}|2541|2557
PMC6094787|strange sensations|Strange sensation|C0423571|0.8235294117647058|{'T184'}|1557|1575
PMC6094787|nasal cavity|Nasal cavity|C0225425|0.8181818181818182|{'T029'}|3780|3792
PMC6094787|examination|Examination|C0031809|0.8|{'T058'}|2034|2045
PMC6094787|application|Application|C0185125|0.8|{'T061'}|3263|3274
PMC6094787|obstruction|Obstruction|C0028778|0.8|{'T033'}|4042|4053
PMC6094790|Surgery|Surgery|C0543467|1.0|{'T061'}|4623|4630
PMC6094790|Then|Then|C1720594|1.0|{'T170'}|4130|4134
PMC6094790|And|And|C1706368|1.0|{'T170'}|3504|3507
PMC6094790|alveolar process|Alveolar process|C0002386|0.8666666666666667|{'T023'}|12624|12640
PMC6094790|alveolar process|Alveolar process|C0002386|0.8666666666666667|{'T023'}|14113|14129
PMC6094790|discrimination|Discrimination|C0012632|0.8461538461538461|{'T041'}|2601|2615
PMC6094790|extract tooth|Extract tooth|C0040440|0.8333333333333334|{'T061'}|2275|2290
PMC6094790|examine|Hexamine|C0025638|0.8333333333333334|{'T109', 'T121'}|6553|6560
PMC6094790|observation|Observation|C0557985|0.8|{'T061'}|5664|5675
PMC6094790|molar tooth|Molar tooth|C0026367|0.8|{'T023'}|5846|5857
PMC6094790|sound tooth|Sound tooth|C0426482|0.8|{'T033'}|11337|11348
PMC6094790|molar tooth|Molar tooth|C0026367|0.8|{'T023'}|11574|11585
PMC6094790|motion|Emotion|C0013987|0.8|{'T041'}|13081|13087
PMC6094792|Blood|Blood|C0005767|1.0|{'T031'}|2063|2068
PMC6094792|And|And|C1706368|1.0|{'T170'}|130|133
PMC6094792|And|And|C1706368|1.0|{'T170'}|257|260
PMC6094792|And|And|C1706368|1.0|{'T170'}|428|431
PMC6094792|And|And|C1706368|1.0|{'T170'}|778|781
PMC6094792|Tis|Tis|C0475413|1.0|{'T033'}|1192|1195
PMC6094792|And|And|C1706368|1.0|{'T170'}|1283|1286
PMC6094792|And|And|C1706368|1.0|{'T170'}|1368|1371
PMC6094792|And|And|C1706368|1.0|{'T170'}|1405|1408
PMC6094792|And|And|C1706368|1.0|{'T170'}|2284|2287
PMC6094792|And|And|C1706368|1.0|{'T170'}|2329|2332
PMC6094792|Now|Now|C1720566|1.0|{'T170'}|2377|2380
PMC6094792|And|And|C1706368|1.0|{'T170'}|2508|2511
PMC6094793|Phosphoric acid|Phosphoric acid|C0031700|1.0|{'T121', 'T197'}|10450|10465
PMC6094793|Application|Application|C0185125|1.0|{'T061'}|1149|1160
PMC6094793|Diseases|Diseases|C0012634|1.0|{'T047'}|9203|9211
PMC6094793|Medicine|Medicine|C0013227|1.0|{'T121'}|13641|13649
PMC6094793|History|History|C0262926|1.0|{'T033'}|8877|8884
PMC6094793|History|History|C5399914|1.0|{'T170'}|8877|8884
PMC6094793|History|History|C0262926|1.0|{'T033'}|10315|10322
PMC6094793|History|History|C5399914|1.0|{'T170'}|10315|10322
PMC6094793|Teeth|Teeth|C0040426|1.0|{'T023'}|8894|8899
PMC6094793|Teeth|Teeth|C0040426|1.0|{'T023'}|9219|9224
PMC6094793|Some|Some|C3540770|1.0|{'T170'}|109|113
PMC6094793|Lime|Lime|C0064990|1.0|{'T121', 'T197'}|10863|10867
PMC6094793|And|And|C1706368|1.0|{'T170'}|10336|10339
PMC6094793|And|And|C1706368|1.0|{'T170'}|15986|15989
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|7971|7986
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|8060|8075
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|8159|8174
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|8469|8484
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|8784|8799
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|9857|9872
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|10683|10698
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|10910|10925
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|11134|11149
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|13293|13308
PMC6094793|phosphoric acid|Phosphoric acid|C0031700|0.9230769230769231|{'T121', 'T197'}|17906|17921
PMC6094793|lower jaw bone|Lower jaw bone|C0024687|0.8461538461538461|{'T023'}|16847|16861
PMC6094793|part of tooth|Part of tooth|C0524814|0.8333333333333334|{'T023'}|9530|9547
PMC6094793|tartaric acids|Tartaric acid|C0075821|0.8333333333333334|{'T109', 'T130'}|10972|10986
PMC6094793|examine|Hexamine|C0025638|0.8333333333333334|{'T109', 'T121'}|9789|9796
PMC6094793|febrile|Afebrile|C0277797|0.8333333333333334|{'T033'}|19464|19471
PMC6094793|inflammation|Inflammation|C0021368|0.8181818181818182|{'T046'}|147|159
PMC6094793|running away|Running away|C0424352|0.8181818181818182|{'T033'}|18004|18016
PMC6094793|hectic fever|Hectic fever|C0277800|0.8181818181818182|{'T033'}|18830|18842
PMC6094793|disease of bones|Disease of bone|C0005940|0.8|{'T047'}|16682|16702
PMC6094793|ventilation|Ventilation|C2945579|0.8|{'T039'}|2595|2606
PMC6094793|application|Application|C0185125|0.8|{'T061'}|3522|3533
PMC6094793|destruction|Destruction|C1261381|0.8|{'T061'}|9495|9506
PMC6094793|sound tooth|Sound tooth|C0426482|0.8|{'T033'}|14816|14827
PMC6094793|application|Application|C0185125|0.8|{'T061'}|17237|17248
PMC6094793|application|Application|C0185125|0.8|{'T061'}|18454|18465
PMC6094793|destruction|Destruction|C1261381|0.8|{'T061'}|18745|18756
PMC6094793|observation|Observation|C0557985|0.8|{'T061'}|19766|19777
PMC6094793|generation|Degeneration|C0011164|0.8|{'T046'}|1593|1603
PMC6094793|generation|Regeneration|C0349676|0.8|{'T058'}|1593|1603
PMC6094793|difference|Indifference|C0085632|0.8|{'T048'}|14216|14226
PMC6094793|employment|Unemployment|C0041674|0.8|{'T033'}|20988|20998
PMC6094793|active|Factive|C1320102|0.8|{'T109', 'T195'}|13774|13780
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|4979|4985
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|7303|7309
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|7539|7545
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|11063|11069
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|13998|14004
PMC6094793|tartar|Tartar|C0011330|0.75|{'T033'}|14103|14109
PMC6094794|Does|Does|C1272751|1.0|{'T033'}|1082|1086
PMC6094794|Does|Does|C1272751|1.0|{'T033'}|1572|1576
PMC6094794|Will|Will|C0042950|1.0|{'T041'}|1840|1844
PMC6094794|And|And|C1706368|1.0|{'T170'}|2031|2034
PMC6094795|English|English|C3540738|1.0|{'T170'}|1421|1428
PMC6094795|English|English|C3540738|1.0|{'T170'}|3254|3261
PMC6094795|English|English|C3540738|1.0|{'T170'}|3298|3305
PMC6094795|destination|Festination|C0231694|0.8|{'T033'}|7541|7552
PMC6094795|active|Factive|C1320102|0.8|{'T109', 'T195'}|1708|1714
"""

# Print current selection with each header in a different color
ASCII_COLORS: List[str] = [
    "\033[91m",  # Red
    "\033[92m",  # Green
    "\033[93m",  # Yellow
    "\033[94m",  # Blue
    "\033[95m",  # Magenta
    "\033[96m",  # Cyan
    "\033[97m",  # White
]

RESET_COLOR = "\033[0m"


def build_nested_lookup(header, rows, selected_headers, unused_headers):
    lookup = {}
    for row in rows:
        current = lookup
        for i, key in enumerate(selected_headers):
            value = row[header.index(key)]
            if i == len(selected_headers) - 1:
                # At the deepest level, create a dict of unused headers
                unused_dict = {h: row[header.index(h)] for h in unused_headers}
                current.setdefault(value, []).append(unused_dict)
            else:
                current = current.setdefault(value, {})
    return lookup


def initialize_paths(project_name: str) -> Tuple[Path, Path]:

    def initialize_csv_to_lookup_root():
        csv_to_lookup_root = Path("/output/csv_to_dict_lookup")
        csv_to_lookup_root.mkdir(parents=True, exist_ok=True)
        return csv_to_lookup_root

    def initialize_config_output_path(csv_to_lookup_root):
        config_output_path: Path = csv_to_lookup_root / "config" / project_name
        config_output_path.mkdir(parents=True, exist_ok=True)
        return config_output_path

    def initialize_lookup_output_path(csv_to_lookup_root):
        lookup_output_path: Path = csv_to_lookup_root / "lookup" / project_name
        lookup_output_path.mkdir(parents=True, exist_ok=True)
        return lookup_output_path

    csv_to_lookup_root: Path = initialize_csv_to_lookup_root()
    config_output_path: Path = initialize_config_output_path(csv_to_lookup_root)
    lookup_output_path: Path = initialize_lookup_output_path(csv_to_lookup_root)
    return config_output_path, lookup_output_path


def persist_config(config_output_path, selected_headers, unused_headers):
    config_dict = {
        "selected_headers": selected_headers,
        "unused_headers": unused_headers,
    }

    config_output_file = config_output_path / "header_config.json"
    with open(config_output_file, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2)
    logger.info(f"\nSaved header config to: {config_output_file}")


def persist_lookup(lookup_output_path, nested_lookup):
    lookup_output_file = lookup_output_path / "nested_lookup.json"
    with open(lookup_output_file, "w", encoding="utf-8") as f:
        json.dump(nested_lookup, f, indent=2)
    logger.info(f"\nSaved nested lookup to: {lookup_output_file}")


def build_config(header, sample_row, config_output_path):
    available_headers = header.copy()

    # 3) set selected_headers=[]
    selected_headers = []

    # 4) Menu-driven selection task:
    unused_headers = []

    while available_headers or selected_headers:
        print("\nAvailable headers:")
        for idx, h in enumerate(available_headers):
            # Find the first non-empty example value for this header
            col_idx = header.index(h)
            example = ""
            if sample_row[col_idx].strip():
                example = sample_row[col_idx]
                break
            print(f"{idx + 1}. {h} (e.g. {example})")
        if selected_headers:
            colored = [
                f"{ASCII_COLORS[i % len(ASCII_COLORS)]}{h}{RESET_COLOR}"
                for i, h in enumerate(selected_headers)
            ]
            print("Current selection:", " -> ".join(colored))
        sel = input(
            f"Select header for level {len(selected_headers) + 1} (enter number, 'd' for done, or 'u' to undo): "
        )
        if sel.lower() == "d":
            print("Selection done.")
            # Track unused headers
            unused_headers = available_headers.copy()
            break
        if sel.lower() == "u":
            if selected_headers:
                undone = selected_headers.pop()
                available_headers.append(undone)
                print(f"Undid selection: {undone}")
            else:
                print("Nothing to undo.")
            continue
        try:
            sel_idx = int(sel) - 1
            if sel_idx < 0 or sel_idx >= len(available_headers):
                print("Invalid selection. Try again.")
                continue
        except ValueError:
            print("Invalid input. Try again.")
            continue
        selected = available_headers.pop(sel_idx)
        selected_headers.append(selected)
        print(f"Selected: {selected}")

    if unused_headers:
        logger.info("\nUnused headers:", ", ".join(unused_headers))

    persist_config(config_output_path, selected_headers, unused_headers)
    return selected_headers, unused_headers


def get_sample_row(rows, min_char_length=3):
    return next(
        row
        for row in rows[1:]
        if all(len(field.strip()) >= min_char_length for field in row)
    )


def pretty_print_nested_lookup(d, indent=0):
    spacing = " " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (dict, list)):
                print(f"{spacing}{repr(k)}:")
                pretty_print_nested_lookup(v, indent + 4)
            else:
                print(f"{spacing}{repr(k)}:{repr(v)},")
    elif isinstance(d, list):
        for item in d:
            pretty_print_nested_lookup(item, indent + 4)
    else:
        print(f"{spacing}{repr(d)}")


if __name__ == "__main__":

    project_name = "test_case_1"
    config_output_path, lookup_output_path = initialize_paths(project_name)

    # 1) Load the file into a CSV reader
    delimeter = "|"
    reader_source = example_csv_data
    header = None
    if Path(reader_source).exists():
        with open(reader_source, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimeter)
            rows = list(reader)
            header = rows[0]
    else:
        reader = csv.reader(io.StringIO(reader_source.strip()), delimiter=delimeter)
        rows = list(reader)
        header = rows[0]
    # Find the first row where each field has at least three characters
    sample_row = get_sample_row(rows)

    data_rows = rows[1:]

    # 2) Add the header fields in order to a list, `available_headers`
    selected_headers, unused_headers = build_config(
        header, sample_row, config_output_path
    )

    # 5) Use the selected headers to efficiently create a nested dictionary lookup structure.
    nested_lookup = build_nested_lookup(
        header, data_rows, selected_headers, unused_headers
    )

    persist_lookup(lookup_output_path, nested_lookup)

    logger.info("\nNested dictionary lookup structure:")

    pretty_print_nested_lookup(nested_lookup)
