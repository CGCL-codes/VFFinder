


VPV_recognition_prompt_template = '''
Task description:Your task is to extract the product phase from the given description, the product phase means the phase that describe about the product and version.
Requirement: Make sure your output are !TOTALLY! extracted from the original INPUT! If you cannot find the corresponding value, just answer "None":

INPUT:Directory traversal vulnerability in RequestUtil.java in Apache Tomcat 6.x before 6.0.45, 7.x before 7.0.65, and 8.x before 8.0.27 allows remote authenticated users to bypass intended SecurityManager restrictions
OUTPUT:Apache Tomcat 6.x before 6.0.45, 7.x before 7.0.65, and 8.x before 8.0.27

INPUT:inversoft prime-jwt version prior to version 1.3.0 or prior to commit 0d94dcef0133d699f21d217e922564adbb83a227 contains an input validation vulnerability
OUTPUT:inversoft prime-jwt version prior to version 1.3.0 or prior to commit 0d94dcef0133d699f21d217e922564adbb83a227

INPUT:{}
OUTPUT:
'''



COMP_recognition_prompt_template = '''Task description:Your task is to identify the component phase from the provided description. The component phase refers to specific parts of the vulnerable software, such as a file/file path, function, class, or library, but not the software as a whole, in the give description the software is {}.

Requirement: Make sure your output are !TOTALLY! extracted from the original INPUT!, follow the example output I give you, !if you can not find the corresponding value, just answer None!:

INPUT:A stack overflow in the XML.toJSONObject of hutool-json v5.8.10 allows attackers to cause a Denial of Service (DoS) via crafted JSON or XML data.
OUTPUT:XML.toJSONObject

INPUT:Archive.java in Junrar before 1.0.1, as used in Apache Tika, is affected by a denial of service vulnerability.
OUTPUT:Archive.java

INPUT:{}
OUTPUT:
'''