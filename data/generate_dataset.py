import csv
import random
import string
import uuid
import hashlib
import base64
import secrets
import json

def generate_random_string(length, charset):
    return ''.join(random.choice(charset) for _ in range(length))

def generate_realistic_context():
    contexts = [
        'API_KEY = "{}"',
        'const apiKey = "{}";',
        'export const TOKEN = "{}";',
        'password: "{}"',
        '"Authorization": "Bearer {}"',
        'client_secret={}',
        '--token {}',
        'DATABASE_URL="postgresql://user:{}@localhost/db"',
        'aws_secret_access_key = "{}"',
        'GITHUB_TOKEN={}'
    ]
    return random.choice(contexts)

def generate_positives(count):
    positives = []
    
    alphanumeric = string.ascii_letters + string.digits
    alphanumeric_hyphen = alphanumeric + '-_'
    hex_chars = string.hexdigits.lower()
    base64_chars = string.ascii_letters + string.digits + '+/='
    
    generators = {
        "github_token": lambda: "ghp_" + generate_random_string(36, alphanumeric),
        "github_classic_token": lambda: generate_random_string(40, hex_chars),
        "aws_key_id": lambda: "AKIA" + generate_random_string(16, string.ascii_uppercase + string.digits),
        "aws_secret_key": lambda: generate_random_string(40, alphanumeric + '+/'),
        "google_api_key": lambda: "AIza" + generate_random_string(35, alphanumeric_hyphen),
        "slack_token": lambda: f"xoxp-{generate_random_string(12, string.digits)}-{generate_random_string(13, string.digits)}-{generate_random_string(24, alphanumeric)}",
        "slack_webhook": lambda: f"xoxb-{generate_random_string(12, string.digits)}-{generate_random_string(24, alphanumeric)}",
        "generic_high_entropy": lambda: secrets.token_urlsafe(random.randint(24, 48)),
        "hex_key_64": lambda: generate_random_string(64, hex_chars),
        "hex_key_32": lambda: generate_random_string(32, hex_chars),
        "jwt_token": lambda: '.'.join([
            base64.b64encode(json.dumps({"typ": "JWT", "alg": "HS256"}).encode()).decode().rstrip('='),
            base64.b64encode(json.dumps({"sub": "1234567890", "name": "John Doe"}).encode()).decode().rstrip('='),
            generate_random_string(43, base64_chars).rstrip('=')
        ]),
        "stripe_key": lambda: f"sk_{'test' if random.random() > 0.5 else 'live'}_" + generate_random_string(24, alphanumeric),
        "stripe_publishable": lambda: f"pk_{'test' if random.random() > 0.5 else 'live'}_" + generate_random_string(24, alphanumeric),
        "mailgun_key": lambda: "key-" + generate_random_string(32, hex_chars),
        "sendgrid_key": lambda: "SG." + generate_random_string(22, alphanumeric_hyphen) + "." + generate_random_string(43, alphanumeric_hyphen),
        "twilio_sid": lambda: "AC" + generate_random_string(32, hex_chars),
        "firebase_key": lambda: "AAAA" + generate_random_string(7, alphanumeric) + ":" + generate_random_string(140, alphanumeric_hyphen),
        "discord_token": lambda: generate_random_string(24, alphanumeric_hyphen) + "." + generate_random_string(6, alphanumeric_hyphen) + "." + generate_random_string(27, alphanumeric_hyphen),
        "telegram_token": lambda: f"{random.randint(100000000, 999999999)}:{generate_random_string(35, alphanumeric_hyphen)}",
        "docker_config": lambda: generate_random_string(random.randint(40, 80), base64_chars),
        "private_key_hex": lambda: generate_random_string(64, hex_chars),  # Common for crypto
        "api_secret": lambda: generate_random_string(random.randint(32, 64), alphanumeric_hyphen),
        "oauth_secret": lambda: generate_random_string(random.randint(40, 80), alphanumeric_hyphen),
    }
    
    for _ in range(count):
        key_type = random.choice(list(generators.keys()))
        secret = generators[key_type]()
        
        if random.random() > 0.3: 
            context = generate_realistic_context()
            secret = context.format(secret)
            
        positives.append(secret)
        
    return positives

def generate_negatives(count):
    negatives = []
    
    generators = {
        "uuid": lambda: str(uuid.uuid4()),
        "sha256_hash": lambda: hashlib.sha256(str(random.random()).encode()).hexdigest(),
        "md5_hash": lambda: hashlib.md5(str(random.random()).encode()).hexdigest(),
        "base64_string": lambda: base64.b64encode(str(random.random()).encode()).decode(),
        "long_variable_name": lambda: '_'.join([secrets.token_hex(4) for _ in range(random.randint(4, 7))]),
        "short_hex_string": lambda: secrets.token_hex(8),
        "commit_hash": lambda: generate_random_string(40, string.hexdigits.lower()),
        "short_commit_hash": lambda: generate_random_string(7, string.hexdigits.lower()),
        "file_checksum": lambda: f"sha256:{generate_random_string(64, string.hexdigits.lower())}",
        "docker_image_id": lambda: f"sha256:{generate_random_string(64, string.hexdigits.lower())}",
        "build_id": lambda: f"build-{random.randint(1000, 9999)}-{generate_random_string(8, string.hexdigits.lower())}",
        "session_id": lambda: f"sess_{generate_random_string(24, string.ascii_letters + string.digits)}",
        "request_id": lambda: f"req_{generate_random_string(16, string.ascii_letters + string.digits)}",
        "transaction_id": lambda: f"txn_{generate_random_string(20, string.ascii_letters + string.digits)}",
        "encrypted_password": lambda: f"$2b$12${generate_random_string(53, string.ascii_letters + string.digits + './')}",  
        "version_string": lambda: f"v{random.randint(1,5)}.{random.randint(0,20)}.{random.randint(0,50)}",
        "base64_encoded_image": lambda: f"data:image/png;base64,{generate_random_string(100, string.ascii_letters + string.digits + '+/=')}",
        "url_safe_token": lambda: generate_random_string(random.randint(16, 32), string.ascii_letters + string.digits + '-_'),
        "filename_hash": lambda: f"{generate_random_string(8, string.ascii_lowercase)}.{random.choice(['jpg', 'png', 'pdf', 'txt'])}",
        "debug_token": lambda: f"debug_{generate_random_string(16, string.ascii_letters + string.digits)}",
        "test_key": lambda: f"test_key_{generate_random_string(20, string.ascii_letters + string.digits)}",
        "mock_secret": lambda: f"mock_{generate_random_string(24, string.ascii_letters + string.digits)}",
        "placeholder": lambda: random.choice([
            "your_api_key_here", "insert_token_here", "replace_with_actual_key",
            "TODO_add_real_token", "example_key_123", "fake_secret_key"
        ]),
    }

    for _ in range(count):
        key_type = random.choice(list(generators.keys()))
        negative = generators[key_type]()
        
        if random.random() > 0.7: 
            context = generate_realistic_context()
            negative = context.format(negative)
            
        negatives.append(negative)
        
    return negatives

def add_edge_cases(count):
    edge_cases = []
    

    edge_cases.extend([
        ("ghp_123", 0),  
        ("AKIA123", 0),  
        ("AIza123", 0),  
        ("sk_test_", 0),  
    ])
    
    for _ in range(count // 4):
        long_string = generate_random_string(random.randint(100, 200), string.ascii_letters + string.digits)
        edge_cases.append((long_string, 0))
    
    for _ in range(count // 4):
        mixed_string = generate_random_string(32, string.ascii_letters + string.digits + "!@#$%^&*()")
        edge_cases.append((mixed_string, 0))
    
    for _ in range(count // 2):
        secret = "ghp_" + generate_random_string(36, string.ascii_letters + string.digits)
        edge_cases.append((secret, 1))
    
    return edge_cases[:count]

if __name__ == "__main__":
    NUM_SAMPLES_PER_CLASS = 2500 
    NUM_EDGE_CASES = 500
    
    print("Generating positive samples (secrets)...")
    positive_samples = generate_positives(NUM_SAMPLES_PER_CLASS)
    
    print("Generating negative samples (false positives)...")
    negative_samples = generate_negatives(NUM_SAMPLES_PER_CLASS)
    
    print("Generating edge cases...")
    edge_cases = add_edge_cases(NUM_EDGE_CASES)
    
    dataset = []
    for sample in positive_samples:
        dataset.append([sample, 1])
        
    for sample in negative_samples:
        dataset.append([sample, 0])
        
    for sample, label in edge_cases:
        dataset.append([sample, label])
        
    random.shuffle(dataset)
    
    total_samples = len(dataset)
    positive_count = sum(1 for _, label in dataset if label == 1)
    negative_count = total_samples - positive_count
    
    print(f"\nDataset Statistics:")
    print(f"Total samples: {total_samples}")
    print(f"Positive samples (secrets): {positive_count}")
    print(f"Negative samples (non-secrets): {negative_count}")
    print(f"Balance ratio: {positive_count/negative_count:.2f}")
    
    output_filename = "secrets_dataset.csv"
    print(f"\nWriting to {output_filename}...")
    
    with open(output_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"]) 
        writer.writerows(dataset)
        
    print("Dataset generation complete!")

    print(f"\nSample positive examples:")
    positives = [row[0] for row in dataset if row[1] == 1][:5]
    for i, example in enumerate(positives, 1):
        print(f"{i}. {example}")
        
    print(f"\nSample negative examples:")
    negatives = [row[0] for row in dataset if row[1] == 0][:5]
    for i, example in enumerate(negatives, 1):
        print(f"{i}. {example}")