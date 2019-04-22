from collections import namedtuple


Endpoint = namedtuple('Endpoint',['name', 'host', 'zone'])

region_to_endpoint = {
      'us-east-2': Endpoint('US East (Ohio)', 's3-website.us-east-2.amazonaws.com', 'Z2O1EMRO9K5GLX'),
      'us-east-1': Endpoint('US East (N. Virginia)', 's3-website-us-east-1.amazonaws.com', 'Z3AQBSTGFYJSTF'),
      'us-west-1': Endpoint('US West (N. California)', 's3-website-us-west-1.amazonaws.com', 'Z2F56UZL2M1ACD'),
      'us-west-2': Endpoint('US West (Oregon)', 's3-website-us-west-2.amazonaws.com', 'Z3BJ6K6RIION7M'),
      'ap-south-1': Endpoint('Asia Pacific (Mumbai)', 's3-website.ap-south-1.amazonaws.com', 'Z11RGJOFQNVJUP'),
      'ap-northeast-3': Endpoint('Asia Pacific (Osaka-Local)', 's3-website.ap-northeast-3.amazonaws.com', 'Z2YQB5RD63NC85'),
      'ap-northeast-2': Endpoint('Asia Pacific (Seoul)', 's3-website.ap-northeast-2.amazonaws.com', 'Z3W03O7B5YMIYP'),
      'ap-southeast-1': Endpoint('Asia Pacific (Singapore)', 's3-website-ap-southeast-1.amazonaws.com', 'Z3O0J2DXBE1FTB'),
      'ap-southeast-2': Endpoint('Asia Pacific (Sydney)	', 's3-website-ap-southeast-2.amazonaws.com', 'Z1WCIGYICN2BYD')

}

"""Asia Pacific (Tokyo)
s3-website-ap-northeast-1.amazonaws.com

Z2M4EHUR26P7ZW
Canada (Central)
s3-website.ca-central-1.amazonaws.com

Z1QDHH18159H29
China (Ningxia)
s3-website.cn-northwest-1.amazonaws.com.cn

Not supported
EU (Frankfurt)
s3-website.eu-central-1.amazonaws.com

Z21DNDUVLTQW6Q
EU (Ireland)
s3-website-eu-west-1.amazonaws.com

Z1BKCTXD74EZPE
EU (London)
s3-website.eu-west-2.amazonaws.com

Z3GKZC51ZF0DB4
EU (Paris)
s3-website.eu-west-3.amazonaws.com

Z3R1K369G5AVDG
EU (Stockholm)
s3-website.eu-north-1.amazonaws.com

Z3BAZG2TWCNX0D
South America (São Paulo)
s3-website-sa-east-1.amazonaws.com

Z7KQH4QJS55S"""


def known_region(region):
    """Return true if region is available"""
    return region in region_to_endpoint

def get_endpoint(region):
    """get the endpoint for the specified region"""
    return region_to_endpoint[region]
