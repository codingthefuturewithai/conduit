---
description: Test MCP endpoints using Claude subprocess with real data
usage: /project:test-mcp [TOOL-NAME] [ADDITIONAL-PARAMS]
example: /project:test-mcp retrieve_confluence_hierarchy "space_key: ASEP"
---

I'll test the MCP tool "$ARGUMENTS" using Claude subprocess.

## Preparing Test Command

The test will use the following Claude subprocess command:

```bash
claude -p "Use the $ARGUMENTS MCP tool. Use the 'saaga' site alias if applicable. Return the results in a clear, formatted manner." --dangerously-skip-permissions
```

## Executing Test

!claude -p "Use the $ARGUMENTS MCP tool. Use the 'saaga' site alias if applicable. Return the results in a clear, formatted manner." --dangerously-skip-permissions

## Next Steps

After the test completes, I'll:
1. Analyze the output for correctness
2. Check if the tool handled parameters properly
3. Verify the response format matches expectations
4. Document any issues or unexpected behaviors

You can also provide specific test scenarios or parameters to test edge cases.