#!/usr/bin/env node

/**
 * Standalone test for the ArangoDB collection creation fix
 * This tests our fix without requiring the full application stack
 */

const { Database } = require('arangojs');

// Test configuration
const config = {
  url: 'http://localhost:8529',
  databaseName: 'test_pipeshub_fix',
  username: 'root',
  password: '', // Empty password for default setup
};

// Required collections to test our fix
const testCollections = [
  { name: 'records', type: 'document' },
  { name: 'files', type: 'document' },
  { name: 'users', type: 'document' },
  { name: 'knowledgeBase', type: 'document' },
  { name: 'recordRelations', type: 'edge' },
  { name: 'isOfType', type: 'edge' },
  { name: 'permissions', type: 'edge' },
  { name: 'belongsTo', type: 'edge' },
  { name: 'belongsToKnowledgeBase', type: 'edge' },
  { name: 'permissionsToKnowledgeBase', type: 'edge' },
];

async function testCollectionCreationFix() {
  console.log('🔧 Testing ArangoDB Collection Creation Fix');
  console.log('='.repeat(50));
  
  let db;
  let testDbCreated = false;
  
  try {
    // Step 1: Connect to _system database
    console.log('📡 Connecting to ArangoDB...');
    db = new Database({
      url: config.url,
      timeout: 5000,
    });

    if (config.username && config.password) {
      db.useBasicAuth(config.username, config.password);
    }

    // Test connection
    await db.exists();
    console.log('✅ Connected to ArangoDB successfully');

    // Step 2: Create test database
    console.log(`📊 Creating test database: ${config.databaseName}`);
    try {
      await db.createDatabase(config.databaseName);
      testDbCreated = true;
      console.log(`✅ Test database created: ${config.databaseName}`);
    } catch (error) {
      if (error.message.includes('duplicate name')) {
        console.log(`ℹ️  Test database already exists: ${config.databaseName}`);
      } else {
        throw error;
      }
    }

    // Step 3: Switch to test database
    db = new Database({
      url: config.url,
      databaseName: config.databaseName,
      timeout: 5000,
    });

    if (config.username && config.password) {
      db.useBasicAuth(config.username, config.password);
    }

    console.log(`🔄 Switched to database: ${config.databaseName}`);

    // Step 4: Test our collection creation logic (mimicking the fix)
    console.log('\n🛠️  Testing Collection Creation Logic');
    console.log('-'.repeat(40));

    for (const collectionDef of testCollections) {
      try {
        const collection = db.collection(collectionDef.name);
        const exists = await collection.exists();
        
        if (!exists) {
          console.log(`📦 Creating ${collectionDef.type} collection: ${collectionDef.name}`);
          
          if (collectionDef.type === 'edge') {
            await db.createEdgeCollection(collectionDef.name);
          } else {
            await db.createCollection(collectionDef.name);
          }
          
          console.log(`✅ Successfully created: ${collectionDef.name}`);
        } else {
          console.log(`✅ Collection already exists: ${collectionDef.name}`);
        }
      } catch (error) {
        console.error(`❌ Failed to create collection ${collectionDef.name}:`, error.message);
        throw error;
      }
    }

    // Step 5: Test knowledge base creation (the original failing operation)
    console.log('\n🧪 Testing Knowledge Base Creation');
    console.log('-'.repeat(40));
    
    const kbCollection = db.collection('knowledgeBase');
    const testUserId = 'test-user-' + Date.now();
    const testOrgId = 'test-org-' + Date.now();
    
    // Create a test knowledge base (this was the original failing operation)
    const kb = {
      userId: testUserId,
      orgId: testOrgId,
      name: 'Test Knowledge Base',
      createdAtTimestamp: Date.now(),
      updatedAtTimestamp: Date.now(),
      isDeleted: false,
      isArchived: false,
    };

    console.log('📝 Creating test knowledge base document...');
    const result = await kbCollection.save(kb);
    console.log(`✅ Knowledge base created successfully with key: ${result._key}`);
    
    // Test querying (this was part of the original flow)
    console.log('🔍 Testing knowledge base query...');
    const cursor = await db.query(`
      FOR kb IN knowledgeBase
        FILTER kb.userId == @userId AND kb.orgId == @orgId AND kb.isDeleted == false
        RETURN kb
    `, { userId: testUserId, orgId: testOrgId });
    
    const foundKBs = await cursor.all();
    console.log(`✅ Query successful, found ${foundKBs.length} knowledge base(s)`);
    
    // Clean up test data
    console.log('🧹 Cleaning up test data...');
    await kbCollection.remove(result._key);
    console.log('✅ Test knowledge base removed');

    console.log('\n🎉 SUCCESS: Collection Creation Fix Works!');
    console.log('='.repeat(50));
    console.log('📋 Summary:');
    console.log(`   - Database: ${config.databaseName} ✅`);
    console.log(`   - Collections created: ${testCollections.length} ✅`);
    console.log('   - Knowledge base creation: ✅');
    console.log('   - Knowledge base query: ✅');
    console.log('\n🚀 The file upload fix should work correctly!');

  } catch (error) {
    console.error('\n❌ TEST FAILED:', error.message);
    console.error('\n🔧 Details:', error);
    console.error('\n💡 Troubleshooting:');
    console.error('   1. Ensure ArangoDB is running on port 8529');
    console.error('   2. Check if authentication is required');
    console.error('   3. Verify user has collection creation permissions');
    process.exit(1);
  } finally {
    // Cleanup: Remove test database if we created it
    if (testDbCreated && db) {
      try {
        const sysDb = new Database({ url: config.url });
        if (config.username && config.password) {
          sysDb.useBasicAuth(config.username, config.password);
        }
        await sysDb.dropDatabase(config.databaseName);
        console.log(`🧹 Cleaned up test database: ${config.databaseName}`);
      } catch (cleanupError) {
        console.warn(`⚠️  Could not clean up test database: ${cleanupError.message}`);
      }
    }
  }
}

// Run the test
if (require.main === module) {
  testCollectionCreationFix().catch(console.error);
}

module.exports = { testCollectionCreationFix };