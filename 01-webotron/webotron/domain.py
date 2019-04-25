# -*- coding: utf-8 -*-

""" Classes for route 53"""
import uuid

class DomainManager:
    """ Manage a route 53 domain"""

    def __init__(self, session):
        """ create domain manager object"""
        self.session = session
        self.client = self.session.client('route53')

    def find_hosted_zones(self, domain_name):
        paginator = self.client.get_paginator('list_hosted_zones')
        for page in paginator.paginate():
            for zone in page['HostedZones']:
                if domain_name.endswith(zone['Name'][:-1]):
                    return zone

        return None

    def create_hosted_zone(self, domain_name):
        zone_name = '.'.join(domain_name.split('.')[-2:]) + '.'     """to split to split the domain name at '.' character
                                                                         and join last two values with '.'"""
        return self.client.create_hosted_zone(
               Name=zone_name,
               CallerReference=str(uuid.uuid4())
              )


    def create_s3_domain_record(self, zone, domain_name, endpoint):

        return self.client.change_resource_record_sets(
            HostedZoneId=zone['Id'],                         #Reference https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
            ChangeBatch={
                 'Comment': 'Created by AWS automation script',
                 'Changes': [
                      {
                      'Action':'UPSERT',
                      'ResourceRecordSet':{
                            'Name': domain_name,
                            'Type': 'A',
                            'AliasTarget': {
                                    'HostedZoneId': endpoint.zone,
                                    'DNSName': endpoint.host,
                                    'EvaluateTargetHealth': False
                                    }
                                }
                            }
                        ]
                    }
                 )

    def create_cf_domain_record(self, zone, domain_name, cf_domain):

      return self.client.change_resource_record_sets(
          HostedZoneId=zone['Id'],                         #Reference https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.change_resource_record_sets
          ChangeBatch={
             'Comment': 'Created by AWS automation script',
             'Changes': [
                  {
                  'Action':'UPSERT',
                  'ResourceRecordSet':{
                        'Name': domain_name,
                        'Type': 'A',
                        'AliasTarget': {
                                'HostedZoneId':'Z2FDTNDATAQYW2',
                                'DNSName': cf_domain,
                                'EvaluateTargetHealth': False
                                }
                            }
                        }
                    ]
                }
             )
