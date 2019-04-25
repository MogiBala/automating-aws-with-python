"""classes for ACM Certificates"""

class CertificateManager:
    """Manage an ACM Certificate"""
    def __init__(self, session):
        self.session = session
        self.client = self.session.client('acm', region_name='us-east-1')


    def cert_matches(self, cert_arn, domain_name):
        cert_details = self.client.describe_certificate(CertificateArn=cert_arn)
        alt_names = cert-details['Certificate']['SubjectiveAlternativeNames']
        for name in alt_names:
            if name == domain_name:                                             #if domain name = example.com
                return True
            if name[0] == '*' and domain_name.endswith(name[1:]):               #if domain name is subdomain.example.com
                return True
        return False

    def find_matching_cert(self, domain_name):
        paginator = self.client.get_paginator('list_certificates')
        for page in paginator.paginate(CertificateStatuses=['ISSUED']):
            for cert in page['CertificateSumaryList']:
                if self.cert_matches(cert['CertificateArn'], domain_name):
                    return cert
        return None
